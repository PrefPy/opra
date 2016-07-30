function submitPref() {
	var prefcolumn = $('#left-sortable');
	var order = "";
    prefcolumn.children().each(function( index ){
        if( $( this ).children().size() > 0 ){
            $( this ).children().each(function( index ){
                order += $( this ).attr('id') + ",";
            });
            order += "|,";
        }
    });
	$('#pref_order').val(order);
	$('#pref_order').submit();
};

function enableSubmission() {
	document.getElementById('submitbutton').disabled = false;
}

function checkStyle(){
    newItem = "<ul class=\"choice1 empty\"></ul>";
    var tier = 1;
    var id = 0;
    $( ".tier" ).each(function( index ) {
        $( this ).remove();
    });
    $( "#left-sortable" ).children().each(function( index ) {
        if( $( this ).children().size() < 1 ){
            $( this ).remove();
        }else{
            $( this ).attr("id", id.toString());
            id += 1;
            $( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
            $( this ).before("<div class=\"tier\">" + tier + "</div>");
            if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
            if( $( this ).children().size() < 2 
                || ( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) )){
                $( this ).children().css( "width", "85%" );
            }else{
                $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
            }
            tier += 1;
            id += 1;
        }
    });
    $( "#left-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
    $( "#right-sortable" ).children().each(function( index ) {
        if( $( this ).children().size() < 1 ){
            $( this ).remove();
        }else{
            $( this ).attr("id", id.toString());
            id += 1;
            $( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
            $( this ).before("<div class=\"tier\">" + tier + "</div>");
            if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
            if( $( this ).children().size() < 2 
                || ( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) )){
                $( this ).children().css( "width", "85%" );
            }else{
                $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
            }
            tier += 1;
            id += 1;
        }
    });
    if($( "#right-sortable" ).children().size() > 0){
        $( "#right-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
    }
    if( $( "#right-sortable" ).children().size() == 0 ){ enableSubmission(); }
}

function moveToPref(obj) {
	var time = 100
	var prefcolumn = $('#left-sortable');
	var currentli = $(obj);
    console.log(obj.id);
	prefcolumn.append(currentli);
    checkStyle();
    if ($('#right-sortable li').length == 0) { enableSubmission(); }
    $('#left-sortable li').each(function(){
        $(this).removeAttr('onclick');
    });
};

function moveAll() {
 	$( '#left-sortable' ).html( $( '#left-sortable' ).html() + $( '#right-sortable' ).html() );
 	$( '#right-sortable' ).html("")
    $('#left-sortable li').each(function(){
        $(this).removeAttr('onclick')
    });
 	checkStyle();
	enableSubmission();
};

$(function() {
    //if the user updates existing preferences, the submit button should be shown
    if ($('#right-sortable li').length == 0) {
        enableSubmission();
    }
});
