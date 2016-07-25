//  Helper JavaScript created for the voting page (detail.html)

$(function() {
    // Google Analytics
    // -----------------------------------------------------------------------
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-81006265-1', 'none');
 //ga('create', 'UA-81006265-1', 'none','DetailTracker');
    ga('send', 'pageview');
 ga('send', 'event', 'Button', 'click', 'left-sortable');
 //ga('DetailTracker.send', 'pageview');
ga(function(tracker) {
    // Logs the tracker created above to the console.
    console.log(tracker);
});
        var form=document.getElementById('left-sortable');
        form.addEventListener('submit', function(event) {

    // Prevents the browser from submiting the form
    // and thus unloading the current page.
    event.preventDefault();

    // Sends the event to Google Analytics and
    // resubmits the form once the hit is done.
    ga('send', 'event', 'Left Form', 'submit', {
        hitCallback: function() {
            form.submit();
        }
    });
});
    // -----------------------------------------------------------------------
    // Google Tag Manager
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-59SLDM');
    // -----------------------------------------------------------------------


    var wholeHeight1 = $('#left-sortable')[0].scrollHeight;
    var wholeHeight2 = $('#right-sortable')[0].scrollHeight;
    if (wholeHeight1 > wholeHeight2) {
        $('#right-sortable').css("height", wholeHeight1);
    } else {
        $('#left-sortable').css("height", wholeHeight2);
    }
    // $('#left-sortable').sortable('refresh');
    // $('#right-sortable').sortable('refresh');
          
    $('.hide1').mouseover(function(){
        $('.ept',this).show();
    });

function enableSubmission() {
    $('#submitbutton').css("display", "inline");
}
          
          
    var oldList, newList, item;
      
    window.setInterval(function(){
    $("ul.choice1").sortable({
       
        start: function(event, ui) {
        //     sortin=-1,
            item = ui.item;
            newList = oldList = ui.item.parent();
            
        },
        
        stop: function(event, ui) {
            var len = $(".choice1").length;
            newItem = "<ul class=\"choice1\"></ul>";
            $( ".choice1" ).each(function( index ) {
                if( $( this ).children().size() < 1 ){
                    $( this ).remove();
                }else{
                    $( this ).before(newItem);
                    if( $( this ).children().size() < 2 ){
                        if( $( this ).attr('class').indexOf('aftersort')>-1 ){ $( this ).removeClass('aftersort'); }
                        $( this ).children().css( "width", "100%" );
                    }else{
                        $( this ).addClass('aftersort');
                        $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
                    }
                }
            });
            $( ".choice1" ).last().after(newItem);
            if( $( "#right-sortable" ).children().size == 0 ){ enableSubmission(); }
            // alert(oldList.attr('id')+" TO "+newList.attr('id'));
        },
           
        change: function(event, ui) {  
            if(ui.sender) newList = ui.placeholder.parent();
        },
        placeholder: "ui-state-highlight",
        connectWith: "ul.choice1",
    }).disableSelection();
    console.log(1);
    }, 1000);
          
});