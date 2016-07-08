document.addEventListener('DOMContentLoaded', function(){
    var vc = document.getElementById('verify_contact');
    if (vc && document.location.hash) {
        vc.code.value = document.location.hash.slice(1);
    }
});
