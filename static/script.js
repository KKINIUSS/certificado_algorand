$( document ).ready(function() {

    setTimeout( function() { $('.hovered').removeClass('hovered')}, 5000);


    $('#js-activate-file').on('click', function(e){
        e.preventDefault();
        $('#js-file').trigger('click');
    });


 $('.join-sertificat').on('click', function(e) {

        const isChecked = !!$('[type="radio"]:checked').length;
        $( ".wrapper-field" ).each(function( index ) {
            if (
                ($(this).find('.form-control').val() == '') ||
                ( !isChecked )
            ) {
                console.log(12000)
                $(this).append('<span class="error">Required field</span>');
                $(this).find('.form-control').css('border', '1px solid red');
                setTimeout( function() { $('.error').remove()}, 1000);
                setTimeout( function() { $('.form-control').css('border', '1px solid transparent')}, 1000);
            }
        });
        e.preventDefault();
        let form = $(this).parents('form'),
        data = $(form).serializeArray();
        $.ajax({
            url: "/join",
            dataType: "json",
            contentType : "application/json",
            data: JSON.stringify(data),
            type: 'POST',
            success: function (data) {
                if (data) {
                    console.log(14000)
                    console.log(data)
                    $('.join-sertificat').addClass('join-success');
                    console.log(15000)
                    $('.msg-access').show('100');
                    $('.msg-access .content-msg a').attr('href', data);
                }
            }
        });

    });

    $('.search-sertificat').on('click', function(e) {

        $( ".wrapper-field" ).each(function( index ) {
            if (
                ($(this).find('.form-control').val() == '')
            ) {
                e.preventDefault();
                $(this).append('<span class="error">Required field</span>');
                $(this).find('.form-control').css('border', '1px solid red');
                setTimeout( function() { $('.error').remove()}, 1000);
                setTimeout( function() { $('.form-control').css('border', '1px solid transparent')}, 1000);
            }
        });
        e.preventDefault();
        let form = $(this).parents('form'),
        data = $(form).serializeArray();
        $.ajax({
            url: "/validator",
            dataType: "json",
            contentType : "application/json",
            data: JSON.stringify(data),
            type: 'POST',
            success: function (data) {
                if (data) {
                    console.log(data)
                    document.querySelectorAll('.item').forEach(e => e.remove())
                    data.forEach(el => {
                        template = `          <div class="wrapper-ico-item">
                            <i class="ico ico-item" style="background-image: url(static/img/greek.svg);"></i>
                        </div>
                        <div class="content-item">
                            <div class="title-item">${el[6]}</div>
                            <div class="date-item">Gradueted: ${el[5]} </div>
                        </div>
                        <div class="actions-item">
                            <a href="#" class="btn btn-links" data-asset=${el[3]} data-name=${el[1]}><i class="ico ico-download"></i></a>
                            <div class="menu-links">
                                <a href="#" download="true">Download PDF</a>
                                <a href="javascript://" data-asset=${el[3]} data-name=${el[1]} onclick="create(this)">Claim NTF</a>
                            </div>
                        </div>`
                        var newDiv = document.createElement('div')
                        newDiv.className = 'item'
                        newDiv.innerHTML = template

                        console.log(1)
                        document.querySelector('.wrapper-result-items').appendChild(newDiv)
                    })
                    $('.close').on('click', function() {
                            let div = document.querySelector(".verify-sertificat")
                            div.classList.remove('active')
                            document.getElementById('claim_nft').className = 'lock'
                            document.getElementById('download_pdf').className = 'lock'
                            document.getElementById('download_pdf').href = '#'
                            document.getElementById('download_pdf').setAttribute('onclick',"return false")
                            document.getElementById('claim_nft').setAttribute('onclick',"return false")
                            $('#claim_nft').attr({'data-asset':'', 'data-address':''})
                            close_popup();
                    });
                    $('.btn-links').on('click', function(e) {
                        e.preventDefault();
                        console.log($(this).data('asset'))
                        $('.verify-sertificat').attr('data-asset', $(this).data('asset'))
                        open_popup('.popup-access');
                    });
                    $('body').on('click', '#layout', function(e) {
                        e.preventDefault();
                        close_popup();
                    });
                }
            }
        });
    });

    $('.verify-sertificat').on('click', function(e) {

        const isChecked = !!$('[type="radio"]:checked').length;
        $( ".wrapper-field" ).each(function( index ) {
            if (
                ($(this).find('.form-control').val() == '')
            ) {
                e.preventDefault();
                $(this).append('<span class="error">Required field</span>');
                $(this).find('.form-control').css('border', '1px solid red');
                setTimeout( function() { $('.error').remove()}, 1000);
                setTimeout( function() { $('.form-control').css('border', '1px solid transparent')}, 1000);
            }

        });
        e.preventDefault();
        let form = $(this).parents('form'),
        data = $(form).serializeArray();
        console.log(data)
        data.push({'aseet-id' : $(this).attr('data-asset')});
        console.log(data)
        $.ajax({
            url: "/access",
            dataType: "json",
            contentType : "application/json",
            data: JSON.stringify(data),
            type: 'POST',
            success: function (data) {
                if (data) {
                    console.log("success")
                    console.log(data)
                    let div = document.querySelector(".verify-sertificat")
                    div.classList.add('active')
                    document.getElementById('claim_nft').className = 'unlock'
                    document.getElementById('claim_nft').removeAttribute("onclick")
                    document.getElementById('claim_nft').setAttribute("onclick", 'create(this)')
                    $('#claim_nft').attr({'data-asset' : $('.verify-sertificat').attr('data-asset'), 'data-address' : data[0], 'data-name' : data[1]})
                    document.getElementById('download_pdf').className = 'unlock'
                    document.getElementById('download_pdf').href = data[0]
                    document.getElementById('download_pdf').removeAttribute("onclick")


                    console.log(1)
                }
            }
        });

    });





    $(".js-musk-number").mask("999 999", {placeholder: " " });

    $('.close-msg').on('click', function(e) {
        e.preventDefault();
        $(this).parents('.msg').hide('100');
    });



/*
    jQuery(function($){
        $(document).mouseup(function (e){ // событие клика по веб-документу
            var div = $(".menu-links"); // тут указываем ID элемента
            if (!div.is(e.target) // если клик был не по нашему блоку
                && div.has(e.target).length === 0) { // и не по его дочерним элементам
                div.hide(); // скрываем его
                $('.btn-links').removeClass('active');
            }
        });
    });
*/

    var granimInstance = new Granim({
        element: '#canvas-basic',
        direction: 'diagonal',  //radial left-right top-bottom radial
        isPausedWhenNotInView: true,
        states : {
            "default-state": {
                gradients: [
                    ['#090D15', '#001A39'],
                    ['#142d4b', '#090D15'],
                    ['#001A39', '#090D15'],
                    ['#090D15', '#142d4b'],
                    ['#090D15', '#2b0569'],
                    ['#090D15', '#301766'],
                ],
                transitionSpeed: 2000
            }
        }
    });

    $('.standarts').on('click', function(e) {
        e.preventDefault();
        open_popup('.popup-standarts');
    });
    $('.btn-links').on('click', function(e) {
        e.preventDefault();
        open_popup('.popup-access');
    });


    $('body').on('click', '#layout', function(e) {
        e.preventDefault();
        close_popup();
    });

    $('.close').on('click', function() {
        close_popup();
    });

});


function open_popup(popup){
    if ($("#layout").length){
        return false;
    }

    let layout = '<div id="layout" style="background: #000000bd; width: 100vw; height: 100vh; position: fixed; z-index: 999; top: 0; left: 0;  opacity: 0; transition: 0.5s; max-width: 100%;"></div>';
    //let popup = $('.popup');
    $('body').append(layout);
    //$('#layout').css({'display' :  'block'});
    $('#layout').show('slow');
    $('body').addClass('fixed');
    $('#layout').css({'opacity' :  '0.8'});
    $(popup).css({'display' :  'block', 'opacity' :  '1' });
    $('.wrapper-page').css({'filter': 'blur(3px)'});
}

function close_popup(){
    let layout = $('#layout');
    let popup = $('.popup');
    //$(layout).css({ 'display': 'none', 'opacity' :  '0'});
    $('#layout').hide('slow');
    $('body').removeClass('fixed');
    $(layout).remove();
    popup.css({'display' :  'none', 'opacity' :  '0' });
    $('.wrapper-page').css({'filter': 'blur(0px)'});
}




var loadFile = function(event) {
    var output = document.getElementById('output');
    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
        URL.revokeObjectURL(output.src);
    }
    $('.custom-theme').show();
};



function create(e) {
   let attr = e.getAttribute('data-asses');
   console.log(attr);
}

