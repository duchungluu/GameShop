$(document).ready(function () {

	$(window).on('message', function (evt) {

		var event = evt.originalEvent;// This needs to be added because jQuery might preprocess the event, which will result in that the script didn't work on Firefox
        evt.preventDefault();
		var url_str = "/game/play/" + curr_game + "/";

		switch (event.data.messageType){

			case "SCORE":
				$.post(url_str,
				{
					type: "SCORE",
					user: curr_usr,
					game: curr_game,
					score: event.data.score
				},
				function (data,status){
					var message = {messageType: "MESSAGE", message: data};
   					var iframe = $('#gamePlayFrame')[0];
					iframe.contentWindow.postMessage(message, curr_url);
   				});
				break;

			case "SAVE":

				$.post(url_str,
				{
					type: "SAVE",
					user: curr_usr,
					game: curr_game,
					data: JSON.stringify(event.data.gameState)
				},
				function (data,status){
					var message = {messageType: "MESSAGE", message: data};
   					var iframe = $('#gamePlayFrame')[0];
					iframe.contentWindow.postMessage(message, curr_url);
   				});
				break;

			case "LOAD_REQUEST":
				$.post(url_str,
				{
					type: "LOAD",
					user: curr_usr,
					game: curr_game
				},
				function (data,status){

                    var message;
					if(data.length > 1){
						var obj = JSON.parse(data);
   						message = {messageType: "LOAD", gameState: obj} ;
					}

  					else{
  						message = {messageType: "MESSAGE", message: "No savefile to be loaded."};
  					}
   					var iframe = $('#gamePlayFrame')[0];
					iframe.contentWindow.postMessage(message, curr_url);
   				});
				break;

		}
	});

	// EVENT HANDLER. JOKA TARKKAILEE DELETE NAPIN PAINALLUSTA.
	// TÄMÄ POISTAA KLIKATUN PELIN TIETOKANNASTA.
	$(".remove_bttn").on('click', function(evt) {

		var url_str = "/game/profile/";
		var curr_game = this.id;
		$.post(url_str,
			{
				type: "REMOVE",
				game_id: curr_game
			},
			function (data,status){
				var message = data;
				alert(message);
				location.reload(forceGet=true);

			});
	});

	// For modifying the game
	$(".modify_bttn").on('click', function(evt) {
		var url_str = "/game/modify_game/"+this.id.toString()+"/";
        window.location.href = url_str;
    });

    // Used to update the available games views according to the selected filters
    function updateFilters() {

        var url_str = "/game/shop/";
		var string = $( "#searchInput" ).val();
		var pR = $( "#priceRangeFilter option:selected" ).text();
		var ord = $( "#orderingFilter option:selected" ).text();
        var genreSel = [];
        $( ".genreOption" ).each(function( index ) {
            if ($( this ).prop('checked')) {
                genreSel.push($( this ).val());
            }
        });

		$.post(url_str,
			{
				searchField: string,
				priceRange: pR,
				ordering: ord,
                genreSelections: genreSel
			},
			function(data, status){
				var message = data;
				$("#availableGamesContainer").html(message);
                $('.rateitajax').rateit({ max: 5, step: 0.1 }); /*The rateit plugin must be reset after ajax call*/
			});
    }

	// Event handlers for detecting change in filter settings
    $( "#searchInput" ).
		keyup(function(e) {
        switch (e.keyCode) {
            case 9:  // Tab
            case 13: // Enter
                updateFilters();
                return false;
            case 37: // Left
                break;
            case 38: // Up
                break;
            case 39: // Right
                break;
            case 40: // Down
                break;
            default:updateFilters();
        }
	});
	$( "#updateFilter" ).click(updateFilters);
	$( "#searchBtn" ).click(updateFilters);
    $( "#orderingFilter" ).change(updateFilters);
    $( "#priceRangeFilter" ).change(updateFilters);
    $( ".genreOption" ).change(updateFilters);

	// EVENT HANDLER, JOKA TARKKAILEE FACEBOOKPOSTIN PAINAMISTA
	$( "#fbPostBtn" )
		.click(function(evt) {
		var url_str = "/game/play/" + curr_game + "/";
		//string = $( "#searchInput" ).val();
		$.post(url_str,
			{
				type: "FBPOST",
				game: curr_game,
				//query: string,
			},
			function(data,status){
				var message = data;
				alert(message);
			});
	});

    //EVENT HANDLER, JOKA TARKKAILEE RATEITIÄ
    $( ".rateit" ).on("rated", function() {
        var value = $(this).rateit('value');
        var url_str = "/game/play/" + curr_game + "/";

        $.post(url_str,
            {
                type: "RATE",
                user: curr_usr,
                game: curr_game,
                newRate: value,
            });
    });

    /* Add a style class to the link that leads to the current page, exclude
     * facebook sign in button */
    $("a[href$='" + location.pathname + "']").not(".btn-social").addClass("active");

    /* Make the game filter sidebar stick to the navbar bottom while scrolling*/
    var navbarHeight = 0; /* This height is not fetched with
                              $('#narbar').height() because it will on small
                              screens return the wrong height*/
    var stickyTop = 50;
    function stickyNav() {

        var length = $('#content').height() - $('#filter').height() - $('.separator').height() + 27;
        var scrollTop = $(window).scrollTop();
        if (isBreakpoint("xs")) {
            $('#filter').css({
                'position': 'relative',
                'top': 0
            });
        }
        else if (scrollTop > length) {
            $('#filter').css({
                'position': 'relative',
                'top': $('#content').height() - $('#filter').height() - $('.separator').height() - 20
            });
        } else if (scrollTop > stickyTop) {
            $('#filter').css({
                'position': 'fixed',
                'top': navbarHeight + 20
            });
            resizeSidebar();
        } else {
            $('#filter').css({
                'position': 'static'
            });
        }
    }

    /* If the sidebar is in fixed position, it's width won't change according
     * to the Bootstrap column to which it belongs to without this call */
    function resizeSidebar() {
        var width = $("#sidebar").width();
        $("#filter").css('width', width);
    }

    /* The sidebar has to be repositioned on scroll*/
    $(window).scroll(stickyNav);

    /* The sidebar and iframe have to be resized on window resize*/
    $(window).resize(function() {
        resizeSidebar();
    });

    /* Check which Bootstrap width mode is active */
    function isBreakpoint( alias ) {
        return $('.device-' + alias).is(':visible');
    }

    /*Use a separate submit button for the buy form*/
    $(document).on("click", "#buyButton", function() {
        $('form#buyForm').submit();
    });

    //$( "#loginForm" ).submit(function( event ) {
        //event.preventDefault();
        //$.post("/game/login/", $('form#loginForm').serialize(), function(data) {
            //console.log("Login");
        //}).fail(function() {
            //alert( "error" );
        //});
    //});

    /*Call some funtions at the end*/
    stickyNav();

    // Enable the automatically hiding navbar */
    $(".navbar-fixed-top").autoHidingNavbar({
        showOnBottom: false
    });

    /* The star rating on the modal is updated with this*/
    $('#myModal').on('shown.bs.modal', function (e) {
        setTimeout(function(){ $('.rateitajax').rateit({ max: 5, step: 0.1 }); }, 50);
    });

});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
