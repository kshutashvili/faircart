/**
 * Created by batman on 09.08.16.
 */
(function( $ ) {
  $.fn.phonemask = function() {

     $(this).inputmask("phone",{'autoUnmask':true,onUnMask: function(maskedValue, unmaskedValue) {
    //do something with the value
        var val = maskedValue.replace(/\(|\)|-/g,'');
        return val}});

  };
})(jQuery);