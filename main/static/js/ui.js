/**
 * Created by batman on 10.08.16.
 */
(function($){
  $.fn.ajaxSendForm= function () {
      var url = $(this).attr('action');
      var data = $(this).serialize();
      $.ajax({
          url:url,
          type:'POST',
          data: data,
          success:function (data) {
              alert(data);
          }
      });

  }
    
})(jQuery);