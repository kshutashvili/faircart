/**
 * Created by batman on 10.08.16.
 */
(function($){

    $.fn.serializeObject = function () {
        var obj = new Object();
        var arr = $(this).serializeArray();
        for (i in arr){
            obj[arr[i]['name']] = arr[i]['value'];
        }
        return obj
  };

  $.fn.ajaxSendForm = function () {
      var url = $(this).attr('action');
      var data = $(this).serializeObject();
      var method = '';
      if($(this).attr('method') == undefined){
          method = 'get'
      }
      else{
          method = $(this).attr('method');
      }

      $.redirect(url,data,method);
      /*$.ajax({
          url:url,
          type:'POST',
          data: data,
          success:function (data, statusText, xhr) {
              alert(data);
              alert(xhr.getResponseHeader('href'));
              console.log(xhr);
              //.location.reload('/');
          }
      });*/

  }
    
})(jQuery);