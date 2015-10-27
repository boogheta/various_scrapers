var fileNumber = 0

run() // Parce que c'est récursif : le run tournera ad libitum

function run(){

  // Ci-dessous, plein de callbacks empilées :)
  // @Guillaume: imagine fort que c'est du chaînage de fonctions et respire un bon coup !

  // Cliquer sur tous les "-> n réponses"
  expandAll_nAnswers(function(){
    
    // Cliquer sur tous les "voir plus de réponses"
    expandAll_seeMoreAnswers(function(){

      // Cliquer sur tous les "voir  plus"
      expandAll_seeMore(function(){

        saveAndClear(function(){

          // Next batch
          expandComments(run)
        })
      })
    })
  })
}

function expandComments(callback){
  var link = artoo.$('.UFIPagerRow a.UFIPagerLink')
  if(link){
    link.simulate('click')
    
    if(callback){
      setTimeout(callback, 10000)
    }
  }
}

function saveAndClear(callback){
  console.log('\n:: Scraping and saving data...')
  var comments = artoo.$('.UFIComment').scrape(
    {
      id: {
        method: function($){
          return $(this).attr('data-reactid')
        }
      }
    , username: {
        sel: '.UFICommentActorName'
      // , method: function($){return $(this).text()}
      }
    , userlink : {
        sel: '.UFICommentActorName' 
      , method: function($){
          return $(this).attr('href') || ''
        }
      }
    , userid: {
        sel: '.UFICommentActorName' 
      , method: function($){
          var splitUrl = ($(this).attr('href') || '').split('/')
          if(splitUrl && splitUrl.length > 0)
            return splitUrl[splitUrl.length - 1]
          return ''
        }
      }
    , text: {
        sel: 'span.UFICommentBody'
      }
    , likes: {
        sel: '.UFICommentActions a.UFICommentLikeButton'
      }
    , datetext: {
        sel: '.UFICommentActions abbr.livetimestamp'
      }
    , datetimestamp: {
        sel: '.UFICommentActions abbr.livetimestamp'
        , method: function($){
          return $(this).attr('data-utime')
        }
      }
    , parent_id: {
        method: function($){
          return $(this).parent().prev().attr('data-reactid') || ''
        }
      }
    }
  )

  artoo.saveCsv(comments, 'Facebook Comments Export ' + (fileNumber++) + '.csv')

  console.log('...saved')

  console.log('\n:: Clear DOM...')

  while(document.querySelectorAll('.UFIReplyList .UFIComment').length > 0){
    document.querySelector('.UFIReplyList .UFIComment').parentNode.removeChild(document.querySelector('.UFIReplyList .UFIComment'))
  }

  while(document.querySelectorAll('.UFIComment').length > 1){
    document.querySelector('.UFIComment').parentNode.removeChild(document.querySelector('.UFIComment'))
  }

  // while(document.querySelectorAll('.UFIReplyList').length > 0){
  //   document.querySelector('.UFIReplyList').parentNode.removeChild(document.querySelector('.UFIReplyList'))
  // }

  console.log('...cleared')

  if(callback)
    callback()
}

function expandAll_nAnswers(callback){
  console.log('\n:: Click on all "n answers" links')
  artoo.autoExpand({
    expand: function($) {
      $('.UFICommentLink:not(:contains("Masquer"))').first().simulate('click')
      console.log('\tunfolding "n answers" link... (' + $('.UFIComment').length + ' comments)')
    },
    canExpand: function($){
      return $('.UFICommentLink:not(:contains("Masquer"))').length > 0
    },
    elements: '.UFIComment',
    throttle: 5000,
    done: function() {
      console.log('\t..."n answers" links unfolded');
      if(callback)
        callback()
    }
  })
}

function expandAll_seeMoreAnswers(callback){
  console.log('\n:: Click on all "see more answers" links')
  artoo.autoExpand({
    expand: function($) {
      $('.UFIPagerLink').first().simulate('click')
      console.log('\tunfolding "see more answers" link... (' + $('.UFIComment').length + ' comments)')
    },
    canExpand: function($){
      return $('.UFIPagerLink').length > 1
    },
    elements: '.UFIComment',
    throttle: 5000,
    done: function() {
      console.log('\t..."see more answers" links unfolded');
      if(callback)
        callback()
    }
  })
}

function expandAll_seeMore(callback){
  console.log('\n:: Click on all "see more" links')
  expandAll_seeMore_simulate()

  function expandAll_seeMore_simulate(){
    if(artoo.$('a.fss').length > 0){
      artoo.$('a.fss').first().simulate('click')
      console.log('\tunfolding "see more" link...')

      setTimeout(expandAll_seeMore_simulate, 250)
    } else {
      console.log('\t..."see more" links unfolded');
      if(callback)
        callback()
    }
  }
}