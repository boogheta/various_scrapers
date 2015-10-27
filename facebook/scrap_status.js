


artoo.autoScroll({
  elements: '._5sem>div',
  done: function() {
    console.log('Finished scrolling three times!');

  },
  timeout:2000
});



data=artoo.scrape("._5sem>div",
		{
			"status_text":{sel:".userContent>p"},
			"status_html":{sel:".userContent>p",method:"html"},
			"image":{sel:".mtm img",attr:"src"},
			"date":{sel:"abbr",attr:"title"},
			"nbLike":{sel:".UFILikeSentenceText",method:
				function($){
					var likestr=$(this).text() || "" ;
					var nb1 = (likestr.match(/et (\d+)/) || [null,"0"])[1];
					if(likestr.indexOf(",")==-1)
						return +nb1
					else
						return +nb1+likestr.split(",").length
				}
			},
			"nbShare":{
				sel:".UFIShareLink",
				method:function($){
					var strShare=$(this).text() || "" ;
					
					var nb2 = (strShare.match(/(\d+) partages/) || [null,"0"])[1];
					return +nb2
				}
			},
			"nbComment":{
				sel:".UFIPagerLink",
				method:function($){
					var strComment=$(this).text() || "" ;
					var nb1=(strComment.match(/Afficher (\d+)/) || [null,"0"])[1];
					if(nb1 > 0)
						return +nb1+2
					else
						return +nb1
				}
			}
		}
	);

artoo.saveCsv(data)
// la mtéhode html ne concatène pas une liste de sélecteur
 