$(function() {

    // Sliding 'more' actions
    $('.share-bar a.more').click(function() {
      if ($("ul.share-bar-more").hasClass('closed')) {
        $('ul.share-bar-more').removeClass('closed');
        $('ul.share-bar-more').addClass('open');
        $('.share-bar').animate({
          "width": "100%"
        }), 2000;
      } else {
        $('ul.share-bar-more').removeClass('open');
        $('ul.share-bar-more').addClass('closed');
        $('.share-bar').animate({
          "width": "340px"
        }), 2000;
      }
    });

});

(function($) {

  // Share plugin
  $.fn.share = function(options) {

    var opts = $.extend({}, $.fn.share.defaults, options);
    var loaded = new Array();
    var url = document.location;

    return this.each(function() {

      // Twitter
      if(opts.provider == "twitter") {
        $(this).replaceWith('<a class="share-twitter-button button" href="https://twitter.com/share?url='+ url +'" target="_blank"></a><div class="share-twitter-count count">0</div>');
        $.getJSON('http://urls.api.twitter.com/1/urls/count.json?url='+url+'&callback=?', function(data) {  
          $('.share-link-twitter .count').text(data.count);
        });  
      }

      // Facebook
      if(opts.provider == "facebook") {
        $(this).replaceWith('<a class="share-facebook-button button" href="http://www.facebook.com/share.php?u='+ url +'" target="_blank"></a><div class="share-facebook-count count">0</div>');
        $.getJSON('http://graph.facebook.com/'+url+'&callback=?', function(data) {  
            $('.share-facebook-count').text(data.shares);
        });    
      }

      // Pinterest
      if(opts.provider == "pinterest") {
        $(this).replaceWith('<a class="share-pinterest-button button" href="http://pinterest.com/pin/create/button/?url='+ url +'" target="_blank"></a><div class="share-pinterest-count count">0</div>');
        $.getJSON('http://api.pinterest.com/v1/urls/count.json?callback=receiveCount&url=' + url, function(data) {  
            $('.share-pinterest-count').text(data.shares);
        });
      }

    });  
  }

  $.fn.share.defaults = {}

})(jQuery);