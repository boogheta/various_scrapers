#!/usr/bin/env node

var fs = require('fs'),
  sandcrawler = require('sandcrawler'),
  logger = require('sandcrawler-logger'),
  dashboard = require('sandcrawler-dashboard'),
  absUrl = function(u){
    return u.replace(/^(http.*?\.com)?\//, 'http://www.meilleursprenoms.com/');
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
    concurrency: 5,
    encoding: "ISO-8859-1",
    proxy: "http://proxy.medialab.sciences-po.fr:3128"
  })
  .throttle(150, 500)
  .urls(function(){
    var urls = [];
    for (var i='A'.charCodeAt(0); i<= 'Z'.charCodeAt(0); i++) {
      var letter = String.fromCharCode(i);
      var url = "http://www.meilleursprenoms.com/prenoms_az/az.php3?page=1&premiere=" + String.fromCharCode(i);
      urls.push({
        url: url + "&sex=%M",
        data: {letter: letter, sex: 'M'}
      });
      urls.push({
        url: url + "&sex=%F",
        data: {letter: letter, sex: 'F'}
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
    output.items = $("[id^=prenAZ] div ul li a").scrape(scraper);

    var next = $(".page-suivante a.page-active").last();
    output.nextPage = (next.length && next.text() === '   >' && output.items.length ? absUrl(next.attr('href')) : null);

    // Scrape names's similars from name's page
    if (!output.items.length)
      output.similars = $(".bloc-detail:has(img[src^='/images/prenom/picto-autre-pren']) .detail p a").scrape(scraper);

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
      }, when = (item.url ? "now" : "later");
      if (item.name)
        job.data.name = item.name
      if (!doneItemUrls[job.url]) {
        doneItemUrls[job.url] = true;
        droid.addUrl(job, when);
      }
    };

    // Stack items pages from search results
    if (res.data.items.length)
      res.data.items.forEach(push_url);
    // otherwise we're in a name's page:
    else {
      // Stack names found via similarities
      if (res.data.similars.length) {
        res.data.similars.forEach(push_url);
        droid.logger.info(res.data.similars.length + ' similar names of ' + req.data.name);
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
    [res.data.nextPage].forEach(push_url);

  });

// Do not redo already saved items urls
var data = [];
try{
  data = require('./meilleursprenoms.com.json');
} catch(e){
}
if (data) {
  results = data;
  data.forEach(function(a){
    doneItemUrls[a.url] = true;
  });
  droid.logger.info('Starting scraping with already ' + Object.keys(doneItemUrls).length + ' items processed');
}
droid.run();

writedata=function(){
  fs.writeFileSync("meilleursprenoms.com.json", JSON.stringify(results, null, 2));
  process.exit(0);
};

process.on("SIGINT", writedata);
process.on("exit", writedata);
