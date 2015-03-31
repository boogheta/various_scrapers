#!/usr/bin/env node

var fs = require('fs'),
  sandcrawler = require('sandcrawler'),
  logger = require('sandcrawler-logger'),
  dashboard = require('sandcrawler-dashboard'),
  absUrl = function(u){
    return u.replace(/^(http.*?\.com)?\//, 'http://www.prenoms.com/');
  },
  logConf = {
    // level: 'verbose',
    pageLog: false
  },
  results = [],
  doneItemUrls = {};

//var droid = sandcrawler.phantomDroid()
var droid = sandcrawler.droid()
  .use(logger(logConf))
  //.use(dashboard({logger: logConf}))
  .config({
    timeout: 30000,
    maxRetries: 5,
    concurrency: 8,
    proxy: "http://proxy.medialab.sciences-po.fr:3128"
  })
  .throttle(150, 500)
  .urls(function(){
    var urls = [];
    for (var i='c'.charCodeAt(0); i<= 'c'.charCodeAt(0); i++) {
      var url = "http://www.prenoms.com/future-maman-idee-prenom-#SEXE#-" + String.fromCharCode(i) + ".html";
      urls.push({
        url: url.replace("#SEXE#", "garcon"),
        data: {sex: 'F'}
      });
      urls.push({
        url: url.replace("#SEXE#", "fille"),
        data: {sex: 'F'}
      });
    }
    return urls;
  }())
  .scraper(function($, done) {
    var output = {};
    var scraper = {
      name: {method: function($){ return $(this).text().trim(); }},
      url: {method: function($){ return absUrl($(this).attr('href'));}}
    };

    // Scrape items from list pages
    output.items = $("table table a[href^='/prenom/']").scrape(scraper);

    output.nextPages = $(".pagination-rcc-prenom a").scrape("href");

    // Scrape names's similars from name's page
    if (!output.items.length)
    {  
      output.similars_M = $(".prenom-idees-genre.Masculin a").scrape(scraper);
      output.similars_F = $(".prenom-idees-genre.Feminin a").scrape(scraper);
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
      // else {
      //   results.filter(function(e){return e.url === job.url}).forEach(function(e){
      //     if(e.sex != job.data.sex)
      //       e.sex="FF"
      //   })
      // }
    };

    // Stack items pages from search results
    if (res.data.items.length)
      res.data.items.forEach(push_url, this);
    // otherwise we're in a name's page:
    else {
      // Stack names found via similarities

      if (res.data.similars_M.length) {
        res.data.similars_M.forEach(push_url, this);
        this.logger.info(res.data.similars_M.length + ' similar names of ' + req.data.name);
      
        res.data.similars_M=res.data.similars_M.slice(0,19);
        results.push({
            url: req.url,
            name: req.data.name,
            sex: "M",
            similars: res.data.similars_M.map(function(a){
              return a.name;
            })
        });
      }

      if (res.data.similars_F.length) {
        res.data.similars_F.forEach(push_url, this);
        this.logger.info(res.data.similars_F.length + ' similar names of ' + req.data.name);
        
        res.data.similars_F=res.data.similars_F.slice(0,19);
        results.push({
            url: req.url,
            name: req.data.name,
            sex: "F",
            similars: res.data.similars_F.map(function(a){
              return a.name;
            })
        });
      }

    }

    // Stack next search page
    //res.data.nextPages.forEach(push_url, this);

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
droid.run(function(err, remains) {
  // TODO Write CSV + errors
});

writedata=function(){
  fs.writeFileSync("prenoms.com.json", JSON.stringify(results, null, 2));
  process.exit(0);
};

process.on("SIGINT", writedata);
process.on("exit", writedata);
