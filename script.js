$( document ).ready(function() {

    setTimeout( function() { $('.hovered').removeClass('hovered')}, 5000);


    $('#js-activate-file').on('click', function(e){
        e.preventDefault();
        $('#js-file').trigger('click');
    });


    $('.join-sertificat').on('click', function(e) {

        const isChecked = !!$('[type="radio"]:checked').length;
        console.log(isChecked);
        $( ".wrapper-field" ).each(function( index ) {
            if (
                ($(this).find('.form-control').val() == '') ||
                ( !isChecked )
            ) {
                e.preventDefault();
                $(this).append('<span class="error">Required field</span>');
                $(this).find('.form-control').css('border', '1px solid red');
                setTimeout( function() { $('.error').remove()}, 1000);
                setTimeout( function() { $('.form-control').css('border', '1px solid transparent')}, 1000);
            }

        });

    });


    $('.search-sertificat').on('click', function(e) {

        const isChecked = !!$('[type="radio"]:checked').length;
        console.log(isChecked);
        $( ".wrapper-field" ).each(function( index ) {
            if (
                ($(this).find('.form-control').val() == '') ||
                ( !isChecked )
            ) {
                e.preventDefault();
                $(this).append('<span class="error">Required field</span>');
                $(this).find('.form-control').css('border', '1px solid red');
                setTimeout( function() { $('.error').remove()}, 1000);
                setTimeout( function() { $('.form-control').css('border', '1px solid transparent')}, 1000);
            }

        });

    });

    $(".js-musk-number").mask("999 999", {placeholder: " " });


    $('.close-msg').on('click', function(e) {
        e.preventDefault();
        $(this).parents('.msg').hide('100');
    });


    $('.btn-links').on('click', function(e) {
        e.preventDefault();
        $('.btn-links.active').removeClass('active');
        $(this).next('.menu-links').show();
        $(this).addClass('active');
        setTimeout( function() {
            $(this).next('.menu-links').hide();
            $(this).removeClass('active');
            }, 2000);
    });


    jQuery(function($){
        $(document).mouseup(function (e){ // событие клика по веб-документу
            var div = $(".menu-links"); // тут указываем ID элемента
            if (!div.is(e.target) // если клик был не по нашему блоку
                && div.has(e.target).length === 0) { // и не по его дочерним элементам
                div.hide(); // скрываем его
                $(this).removeClass('active');
            }
        });
    });


});

var loadFile = function(event) {
    var output = document.getElementById('output');
    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
        URL.revokeObjectURL(output.src);
    }
    $('.custom-theme').show();
};


