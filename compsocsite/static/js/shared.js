function submitPref() {
	var prefcolumn = $('#left-sortable');
	var order_empty = prefcolumn.sortable("toArray");
	var order = [];
    $(prefcolumn).children().each(function( index ){
        if( $( this ).children().size() > 0 ){
            $( this ).children().each(function( index ){
                order.push($( this ).attr('id'));
            });
        }
    });
	$('#pref_order').val(order.join(","));
    alert(order.join(","));
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
            if( $( this ).children().size() < 2 ){
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
            if( $( this ).children().size() < 2 ){
                $( this ).children().css( "width", "85%" );
            }else{
                $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
            }
            tier += 1;
            id += 1;
        }
    });
    $( "#right-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
    if( $( "#right-sortable" ).children().size == 0 ){ enableSubmission(); }
}

function moveToPref(obj) {
	var time = 100
	var prefcolumn = $('#left-sortable');
    $('#left-sortable li').each(function(){
        $(this).removeAttr('onclick')
    });
	var currentli = document.getElementById(obj.id);
    console.log(obj.id);
	setTimeout(function() {
		prefcolumn.append(currentli);
//		prefcolumn.sortable('refresh');
		if ($('#right-sortable li').length == 0) {
			enableSubmission();
		}
        checkStyle();
	}, time);

};

function moveAll() {
	// var time = 100;
	// var ul = document.getElementById('right-sortable');
	// var items = ul.getElementsByTagName("li");
	// var len = items.length;
	// var prefcolumn = $('#left-sortable');
	// for (var i = 0; i < len; i++) {
	// 	jQuery("#" + items[i].id).addClass("greybackground");
	// }
	// setTimeout(function() {
	// 	for (var i = 0; i < len; i++) {
	// 		prefcolumn.append(items[0]);
	// 	}
	// 	setTimeout(function() {
	// 		var ul = document.getElementById('left-sortable');
	// 		var items = ul.getElementsByTagName("li");
	// 		var len = items.length;

	// 		for (var i = 0; i < len; i++) {
	// 			jQuery("#" + items[i].id).removeClass("greybackground", time);
	// 		}
	// 		prefcolumn.sortable('refresh');
	// 	}, time)
	// }, time)
 	$( '#left-sortable' ).html( $( '#left-sortable' ).html() + $( '#right-sortable' ).html() );
 	$( '#right-sortable' ).html("")
    // $('#left-sortable li').each(function(){
    //     $(this).removeAttr('onclick')
    // });
 	checkStyle();
	enableSubmission();
};

$(function() {
    //if the user updates existing preferences, the submit button should be shown
    if ($('#right-sortable li').length == 0) {
        enableSubmission();
    }

    
    //$("list-group-item").sortable();
	// $("#left-sortable, #right-sortable").sortable({
 // //        start: function(event, ui) {
 // //        //     sortin=-1,
 // //            item = ui.item;
 // //            newList = oldList = ui.item.parent();
            
 // //        },
        
 // //        stop: function(event, ui) {
 // //            if(oldList.attr('id')!=newList.attr('id') && newList.children().size()>1){
 // //                newList.addClass('aftersort');
 // //                newList.children().css( "width", "40%" );
 // //                newList.children().css( "display", "inline-block" );
 // //            } 
            
 // //            //no ul background when ul has only one li
 // //            if(oldList.attr('class').indexOf('aftersort')>-1 && oldList.children().size()<=2){
 // //                oldList.removeClass('aftersort');    
 // //            }
 // //            checkStyle();
 // //            // alert(oldList.attr('id')+" TO "+newList.attr('id'));
 // //        },
           
 // //        change: function(event, ui) {  
 // //            if(ui.sender) newList = ui.placeholder.parent();
 // //        },
	// // 	//placeholder : "ui-sortable-placeholder",
	// // 	containment : "document",
 // //        connectWith : "#right-sortable",
       
 //        start: function(event, ui) {
 //            item = ui.item;
 //            newList = oldList = oL = ui.item.parent();
 //        },
        
 //        stop: function(event, ui) {
 //            var len = $(".choice1").length;
 //            newItem = "<ul class=\"choice1 empty\"></ul>";
 //            var tier = 1;
 //            $( ".tier" ).each(function( index ) {
 //                $( this ).remove();
 //            });
 //            $( ".choice1" ).each(function( index ) {
 //                if( $( this ).children().size() < 1 ){
 //                    $( this ).remove();
 //                }else{
 //                    $( this ).before(newItem);
 //                    $( this ).before("<div class=\"tier\">" + tier + "</div>");
 //                    if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
 //                    if( $( this ).children().size() < 2 ){
 //                        $( this ).children().css( "width", "85%" );
 //                    }else{
 //                        $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
 //                    }
 //                    tier += 1;
 //                }
 //            });
 //            $( ".choice1" ).last().after(newItem);
 //            if( $( "#right-sortable" ).children().size == 0 ){ enableSubmission(); }
 //            // alert(oldList.attr('id')+" TO "+newList.attr('id'));
 //        },
           
 //        change: function(event, ui) {  
 //            if(ui.sender){
 //                newList = ui.placeholder.parent();
 //                newItem = "<ul class=\"choice1 empty line\"></ul>";
 //                var tier = 1;
 //                prevEmpty = false;
 //                $( ".tier" ).each(function( index ) {
 //                    $( this ).remove();
 //                });
 //                $( ".line" ).each(function( index ) {
 //                    $( this ).remove();
 //                });
 //                $( ".choice1" ).each(function( index ) {
 //                    if( $( this ).children().size() < 1){
 //                        $( this ).addClass('empty');
 //                    }else{
 //                        if( $( this ).attr('class').indexOf('empty')>-1 ){
 //                            $( this ).before(newItem);
 //                            $( this ).after(newItem);
 //                            $( this ).removeClass('empty');
 //                        }
 //                        if( $( this ).children().size() < 2 ){
 //                            $( this ).children().css( "width", "85%" );
 //                        }else{
 //                            $( this ).children().css( "width", "40%" ).css( "display", "inline-block" );
 //                        }
 //                        $( this ).before("<div class=\"tier\">" + tier + "</div>");
 //                        tier += 1;
 //                    }
 //                });
 //                if( $(newList).children().size() > 1 ){ $( ui.item ).css("width", "40%"); }
 //                else{ $( ui.item ).css("width", "85%"); }
 //            }
 //        },
 //        placeholder: "ui-state-highlight",
 //        containment: "document",
 //        connectWith: "ul.choice1, ul.empty",
	// });

	// $("#left-sortable, #right-sortable").disableSelection();
});
