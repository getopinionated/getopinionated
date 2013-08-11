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
	clickedButton.toggleClass(clickedClass);
	otherButton.removeClass(otherClass);
	$.post("/proposals/ajax/updownvote/{}/{}/".format(pk, updown), function(data) {
		$("#updownvote-score-"+pk).html(data);
	});
}

function proposalvote_send(proposalslug, score, login_link) {
	// special case: not logged in
	if(login_link) {
		$("#vote_messages").html(
			'<div class="alert alert-error">\
			    <button type="button" class="close" data-dismiss="alert">&times;</button>\
			    <div>You have to be logged in to vote. <a href="{}">Click here to log in</a>.</div>\
			</div>'.format(login_link)
		);
		return;
	}
	// regular case: logged in
	var clickedButtonId = "votebutton_"+score;
	var clickedButton = $('#' + clickedButtonId);
	var otherButtons = $(".votebuttons div.btn:not(#{})".format(clickedButtonId));
	otherButtons.removeClass('btn-primary');
	otherButtons.addClass('btn-info');
	clickedButton.toggleClass('btn-primary');
	clickedButton.toggleClass('btn-info');
	$.post("/proposals/ajax/vote/{}/{}/".format(proposalslug, score), function(data) {
		var dataLines = data.split('\n');
		var msgtype = dataLines[0];
		var message = dataLines[1];
		var alert_class = (msgtype == 'success') ? 'alert-success' : 'alert-error';
		$("#vote_messages").html(
			'<div class="alert {}">\
			    <button type="button" class="close" data-dismiss="alert">&times;</button>\
			    <div>{}</div>\
			</div>'.format(alert_class, message)
		);
	})
}
