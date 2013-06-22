favim = "/static/images/favorite.png"
nofavim = "/static/images/nofavorite.png"

function favorite_send(slug) {

	if(document.getElementById("favorite-"+slug).src.indexOf(favim) != -1){
		document.getElementById("favorite-"+slug).src=nofavim;
	}else{
		document.getElementById("favorite-"+slug).src=favim;
	}
	$.post("/proposals/ajax/favorite/"+slug, function(data) {
		if(data == "0"){
			document.getElementById("favorite-"+slug).src=nofavim;
		}else{
			document.getElementById("favorite-"+slug).src=favim;
		}
	});
}