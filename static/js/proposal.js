favim = "/static/images/favorite.png"
nofavim = "/static/images/nofavorite.png"

function favorite_send(slug) {
	var icon = $("#favorite-"+slug);
	if(icon.attr("src").indexOf(favim) != -1){
		icon.attr("src", nofavim);
	}else{
		icon.attr("src", favim);
	}
	$.post("/proposals/ajax/favorite/{}/".format(slug), function(data) {
		if(data == "0"){
			icon.attr("src", nofavim);
		}else{
			icon.attr("src", favim);
		}
	});
}

function endorse_send(slug) {
	$("#endorse-"+slug).toggleClass("btn-success");
	$.post("/proposals/ajax/endorse/{}/".format(slug), function(data) {
		$("#endorse-score").html(data);
	});
}

/**
 * updownvote_send()
 *
 * @arg updown: should be either 'up' or 'down'
 */
function updownvote_send(pk, updown) {
	var clickedButton = (updown == 'up') ? $("#upvote-"+pk) : $("#downvote-"+pk);
	var otherButton = (updown == 'down') ? $("#upvote-"+pk) : $("#downvote-"+pk);
	var clickedClass = (updown == 'up') ? "btn-success" : "btn-danger";
	var otherClass = (updown == 'down') ? "btn-success" : "btn-danger";
	// clickedButton.toggleClass(clickedClass); // TODO: ability to cancel updownovte
	clickedButton.addClass(clickedClass);
	otherButton.removeClass(otherClass);
	$.post("/proposals/ajax/updownvote/{}/{}/".format(pk, updown), function(data) {
		$("#updownvote-score-"+pk).html(data);
	});
}
