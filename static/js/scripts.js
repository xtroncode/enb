$(document).ready(function(){

$('#characterLeft').html('<p><span class="badge">1000</span> characters left</p>');
$('#description').keyup(function () {
    var max = 1000;
    var len = $(this).val().length;
    if (len >= max) {
        $('#characterLeft').html('<p>You have reached the limit</p>');
    } else {
        var ch = max - len;
        $('#characterLeft').html('<p><span class="badge"> '+ ch +'</span> characters left</p>');
    }

  });
//$('.scroll').jscroll();
  $(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() == $(document).height()) {

     var nexturl=$('a.nexturl:last')[0].href;
     if($('a.nexturl:last')[0].href != window.location.href){
       $.get(nexturl,function(data) {$('.scrolldiv').append(data);});
       }
    $('.description').each(function() {
    $(this).html(urlify($(this).text()));
});

   }
});



$('.description').each(function() {
    $(this).html(urlify($(this).text()));
});


});

function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url + '">' + url + '</a>';
    })
   }


