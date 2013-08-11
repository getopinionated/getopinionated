favim = "/static/images/favorite.png"
nofavim = "/static/images/nofavorite.png"

function favorite_send(slug) {

	if(document.getElementById("favorite-"+slug).src.indexOf(favim) != -1){
		document.getElementById("favorite-"+slug).src=nofavim;
	}else{
		document.getElementById("favorite-"+slug).src=favim;
	}
	$.post("/proposals/ajax/favorite/{}/".format(slug), function(data) {
		if(data == "0"){
			document.getElementById("favorite-"+slug).src=nofavim;
		}else{
			document.getElementById("favorite-"+slug).src=favim;
		}
	});
}

function endorse_send(slug) {

	if(document.getElementById("endorse-"+slug).className.indexOf("btn-success") != -1){
		document.getElementById("endorse-"+slug).className = document.getElementById("endorse-"+slug).className.replace(/\bbtn-success\b/,'');
	}else{
		document.getElementById("endorse-"+slug).className += " btn-success";
	}
	$.post("/proposals/ajax/endorse/{}/".format(slug), function(data) {
		document.getElementById("endorse-score").innerHTML=data;
	});
}

function upvote_send(pk) {
	if(document.getElementById("upvote-"+pk).className.indexOf("btn-success") == -1){
		document.getElementById("downvote-"+pk).className = document.getElementById("downvote-"+pk).className.replace(/\bbtn-danger\b/,'');
		document.getElementById("upvote-"+pk).className += " btn-success";
	}
	$.post("/proposals/ajax/updownvote/{}/up/".format(pk), function(data) {
		document.getElementById("updownvote-score-"+pk).innerHTML=data;
	});
}


function downvote_send(pk) {
	if(document.getElementById("downvote-"+pk).className.indexOf("btn-danger") == -1){
		document.getElementById("upvote-"+pk).className = document.getElementById("upvote-"+pk).className.replace(/\bbtn-success\b/,'');
		document.getElementById("downvote-"+pk).className += " btn-danger";
	}
	$.post("/proposals/ajax/updownvote/{}/down/".format(pk), function(data) {
		document.getElementById("updownvote-score-"+pk).innerHTML=data;
	});
}