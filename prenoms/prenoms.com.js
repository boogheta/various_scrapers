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
    proxy: "http://proxy.medialab.sciences-po.fr:3128"
  })
  .throttle(150, 500)
  .urls(function(){
    var urls = [];
    for (var i='a'.charCodeAt(0); i<= 'z'.charCodeAt(0); i++) {
      var url = "http://www.prenoms.com/future-maman-idee-prenom-#SEXE#-" + String.fromCharCode(i) + ".html";
      urls.push({
        url: url.replace("#SEXE#", "garcon"),
        data: {sex: 'M'}
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
      output.similars = $("#autres-idees-prenoms a").scrape(scraper);

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
    };

    // Stack items pages from search results
    if (res.data.items.length)
      res.data.items.forEach(push_url, this);
    // otherwise we're in a name's page:
    else {
      // Stack names found via similarities
      if (res.data.similars.length) {
        res.data.similars.forEach(push_url, this);
        this.logger.info(res.data.similars.length + ' similar names of ' + req.data.name);
      }
      results.push({
        url: req.url,
        name: req.data.name,
        sex: req.data.sex,
        similars: res.data.similars.map(function(a){
          return a.name;
        })
      });
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
droid.run(function(err, remains) {
  // TODO Write CSV + errors
});

process.on("exit", function(){
  fs.writeFileSync("prenoms.com.json", JSON.stringify(results, null, 2));
});
