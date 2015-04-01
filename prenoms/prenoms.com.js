#!/usr/bin/env node

var fs = require('fs'),
  sandcrawler = require('sandcrawler'),
  logger = require('sandcrawler-logger'),
  dashboard = require('sandcrawler-dashboard'),
  absUrl = function(u){
    return u.replace(/^(http.*?\.com)?\//, 'http://www.prenoms.com/');
  },
  logConf = {
    level: 'verbose',
    pageLog: false
  },
  results = [],
  doneItemUrls = {};


//var droid = sandcrawler.phantomDroid()
var droid = sandcrawler.droid()
  //.use(logger(logConf))
  .use(dashboard({logger: logConf}))
  .config({
    timeout: 30000,
    maxRetries: 5,
    concurrency: 8,
    encoding: "ISO-8859-1",
    proxy: "http://proxy.medialab.sciences-po.fr:3128"
  })
  .throttle(150, 500)
  .urls(function(){
    var urls = [];
    for (var i='a'.charCodeAt(0); i<='z'.charCodeAt(0); i++) {
      var letter = String.fromCharCode(i);
      var url = "http://www.prenoms.com/future-maman-idee-prenom-#SEXE#-" + String.fromCharCode(i) + ".html";
      urls.push({
        url: url.replace("#SEXE#", "garcon"),
        data: {letter: letter.toUpperCase(), sex: 'M'}
      });
      urls.push({
        url: url.replace("#SEXE#", "fille"),
        data: {letter: letter.toUpperCase(), sex: 'F'}
      });
    }
    return urls;
  }())
  .scraper(function($, done) {
    var output = {};
    var scraper = {
      name: {method: function($){ return $(this).text().trim(); }},
      url: {method: function($){ return absUrl($(this).attr('href'));}},
      weight: {method: function($){ 
        var class_to_weight={p01:15,p02:20,p03:12,p04:15,p05:15}
        return class_to_weight[$(this).attr("class")] || 0;
        }
      },
      style_class: {attr: "class"}
    };


    // Scrape items from list pages
    output.items = $("table table a[href^='/prenom/']").scrape(scraper);

    output.nextPages = $(".pagination-rcc-prenom a").scrape("href");

    // Scrape names's similars from name's page
    if (!output.items.length) {  
      output.similars_M = $(".prenom-idees-genre.Masculin a").scrape(scraper);
      output.similars_F = $(".prenom-idees-genre.Feminin a").scrape(scraper);
      output.years_frequencies = $("area").scrape(function(){
        return +$(this).attr("alt").split(" ")[3]
      });
    }
    done(null, output);
  })
  .result(function(err, req, res) {
    if (err)
      return req.retryNow();

    var push_url = function(item){
      if (!item) return;
      var job = {
        url: item.url || item,
        data: {sex: req.data.sex}
      };
      if (item.name)
        job.data.name = item.name
      if (!doneItemUrls[job.url]) {
        doneItemUrls[job.url] = true;
        this.addUrl(job);
      }
    }, add_similars = function(res, sex) {
      if (!res.data["similars_"+sex].length)
        return;
      // Stack names found via similarities
      res.data["similars_"+sex].forEach(push_url, this);
      this.logger.info(res.data["similars_"+sex].length + ' similar ' + sex + ' names of ' + req.data.name);
    
      results.push({
        url: req.url,
        name: req.data.name,
        sex: sex,
        similars: res.data["similars_"+sex]
          .slice(0,19)
          .map(function(a){
            return {
              name: a.name,
              weight: a.weight,
              style_class: a.style_class
            };
          }),
          years_frequencies: res.data.years_frequencies
      });
    };

    // Stack items pages from search results
    if (res.data.items.length)
      res.data.items.forEach(push_url, this);
    // otherwise we're in a name's page:
    else {
      this.add_similars(res, "M");
      this.add_similars(res, "F");
    }

    // Stack next search page
    res.data.nextPages.forEach(push_url, this);

  });

// Do not redo already saved items urls
var data = [];
try{
  data = require('./prenoms.com.json');
} catch(e){

}
if (data) {
  results = data;
  data.forEach(function(a){
    doneItemUrls[a.url] = true;
  });
  droid.logger.info('Starting scraping with already ' + Object.keys(doneItemUrls).length + ' items processed');
}
droid.run()

writedata=function(){
  fs.writeFileSync("prenoms.com.json", JSON.stringify(results, null, 2));
  process.exit(0);
};

process.on("SIGINT", writedata);
process.on("exit", writedata);
