/*** example input ***
 * var timelineData = {
 *     "start_day": 1000,
 *     "center_day": 1010.5,
 *     "end_day": 1040,
 *     "left": {
 *         "caption": "voting started on ...",
 *         "color": "#999",
 *         "proposals": [
 *             ["Dummy proposal cut...", "http://google.com", 1010.2, "10 May"],
 *             ["Dummy proposal cut...", "http://google.com", 1010.3, "10 May"],
 *         ]
 *     },
 *     "right": {
 *         "caption": "voting ends on ...",
 *         "color": "#000",
 *         "proposals": [
 *             ["Dummy proposal cut...", "http://google.com", 1010.8, "10 May"],
 *             ["Dummy proposal cut...", "http://google.com", 1013.3, "13 May"],
 *         ]
 *     }
 * };
 */


/*** settings ***/
var TIMELINE_TOP_Y = 45;
var TIMELINE_HEIGHT = 66.5; // added 0.5 so lines fall on half pixels
// see http://stackoverflow.com/questions/9311428/draw-single-pixel-line-in-html5-canvas
var BG_COL = "#eee";
var PROPOSAL_FONT_SIZE = 14;
var PROPOSAL_SPACE_Y = 20;
var DAY_LINE_HEIGHT = 10;
/*** derived constants ***/
var TIMELINE_BOTTOM_Y = TIMELINE_TOP_Y + TIMELINE_HEIGHT;
var TIMELINE_CENTER_Y = (TIMELINE_TOP_Y + TIMELINE_BOTTOM_Y)/2;

/*** global variables ***/
var links = null;
var ctx = null;
var canvas = null;
var interpretedTimelineData = null;
function drawTimeline(timelineData){
    /*** init vars ***/
    if(interpretedTimelineData == null) {
        interpretedTimelineData = new DataInterpeter(timelineData);
        canvas = $('#timeline')[0];
        ctx = canvas.getContext("2d");
        links = new Links();
    }
    var data = interpretedTimelineData;
    var center_x = data.dayToPx(data.center_day);

    /*** fix width and horizontal position ***/
    //$("#timeline").offset({left:0, relativeTo: "body"});
    canvas.width = window.innerWidth;

    /*** background ***/
    ctx.fillStyle = BG_COL;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    /*** timeline ***/
    ctx.fillStyle = "#ccc";
    ctx.fillRect (0, TIMELINE_TOP_Y, canvas.width, TIMELINE_HEIGHT);

    /*** "now" ***/
    // line
    ctx.beginPath();
    ctx.strokeStyle = "#000";
    ctx.moveTo(center_x, TIMELINE_TOP_Y-10);
    ctx.lineTo(center_x, TIMELINE_BOTTOM_Y);
    ctx.closePath();
    ctx.stroke();
    // text
    ctx.fillStyle = "#000";
    ctx.font = "bold 14px verdana";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText("now", center_x, TIMELINE_TOP_Y-10);

    /*** categories ***/
    var textAlign = {
        "left": "right",
        "right": "left",
    };
    var offSgn = {
        "left": -1,
        "right": 1,
    };
    ctx.font = "18px verdana";
    ctx.textBaseline = "middle";
    ["left", "right"].forEach(function(key){
        ctx.fillStyle = data[key].color;
        ctx.textAlign = textAlign[key];
        ctx.fillText(data[key].caption, center_x + offSgn[key]*20, TIMELINE_CENTER_Y-9);
    });

    /*** day lines ***/
    for(var day = data.start_day+1; day < data.end_day; day++) {
        if(day == data.center_day)
            continue;
        var x = data.dayToPx(day);
        ctx.beginPath();
        ctx.strokeStyle = (day < data.center_day) ? data['left'].color :
            data['right'].color;
        ctx.moveTo(x, TIMELINE_BOTTOM_Y - DAY_LINE_HEIGHT/2);
        ctx.lineTo(x, TIMELINE_BOTTOM_Y + DAY_LINE_HEIGHT/2);
        ctx.stroke();
        ctx.closePath();
    }

    /*** proposals ***/
    var dateAdder = new DateAdder();
    var proposalHeightHelper = new ProposalHeightHelper();
    var neededHeight = Math.round(TIMELINE_BOTTOM_Y + TIMELINE_TOP_Y); // same margin as top
    ["left", "right"].forEach(function(key){
        var N = data[key].proposals.length;
        for(var i = 0; i < N; i++){
            // get vars
            var ii = (key == "left") ? i : N - i - 1; // reverse order if right
            var proposal = data[key].proposals[ii];
            var x = data.dayToPx(proposal.day);
            // get link position
            Link.setStyle();
            var linkWidth = ctx.measureText(proposal.text).width;
            var linkX = x + offSgn[key]*14;
            linkX -= (key == "left") ? linkWidth : 0;
            // check if this is still on screen
            if(linkX < 0 || linkX + linkWidth > canvas.width)
                continue;
            // get link Y
            INT_MARGIN = 3;
            var interval = (key == "left") ?
                new Interval(linkX - INT_MARGIN, x + INT_MARGIN) :
                new Interval(x - INT_MARGIN, linkX + linkWidth + INT_MARGIN);
            var level = proposalHeightHelper.addAndGetLevel(interval, x);
            var y = TIMELINE_BOTTOM_Y + PROPOSAL_SPACE_Y*(level+1);
            var linkY = y - PROPOSAL_FONT_SIZE/2;
            // add link
            var link = new Link(linkX, linkY, linkWidth, PROPOSAL_FONT_SIZE,
                proposal.text, proposal.linkUrl, data[key].color, "#00F");
            links.push(link);
            link.redraw();
            // line
            ctx.beginPath();
            ctx.strokeStyle = data[key].color;
            ctx.moveTo(x, TIMELINE_BOTTOM_Y);
            ctx.lineTo(x, y);
            ctx.lineTo(x + offSgn[key]*10, y);
            ctx.stroke();
            ctx.closePath();
            // date
            dateAdder.add(proposal.day, data.dayToPx(proposal.day),
                proposal.date, data[key].color);
            // enlarge canvas height to make sure it is shown
            var marginBottom = 20;
            var bottomY = linkY + PROPOSAL_FONT_SIZE;
            neededHeight = Math.round(Math.max(neededHeight, bottomY + marginBottom));
        }
    });

    // redraw with right height
    if(canvas.height != neededHeight) {
        canvas.height = neededHeight;
        return drawTimeline(timelineData, true);
    }

    // add mouse listeners
    canvas.addEventListener("mousemove", links.onMouseMove, false);
    canvas.addEventListener("click", links.onClick, false);
}

/*** timelineData interpreter ***/
function DataInterpeter(timelineData) {
    function Proposal(dataLine) {
        this.text = dataLine[0];
        this.linkUrl = dataLine[1];
        this.day = dataLine[2];
        this.date = dataLine[3];
    }
    for (var property in timelineData) {
        this[property] = timelineData[property];
    }
    ["left", "right"].forEach(function(key){
        var proposals = timelineData[key].proposals;
        for(var i = 0; i < proposals.length; i++)
            proposals[i] = new Proposal(proposals[i]);
    });
    this.dayToPx = function(day) {
        var startDay = this.start_day;
        var endDay = this.end_day;
        var frac = (day - startDay) / (endDay - startDay);
        var x = frac * canvas.width;
        return Math.round(x - 0.5) + 0.5; // added 0.5 so lines fall on half pixels
        // see http://stackoverflow.com/questions/9311428/draw-single-pixel-line-in-html5-canvas
    }
}

/*** helper class ***/
function Interval(start, end) {
    this.start = start;
    this.end = end;
    this.has = function(x) {
        return this.start <= x && x <= this.end;
    }
    this.collidesWith = function(interval) {
        return this.has(interval.start) || this.has(interval.end) || interval.has(this.start);
    }
}

/*** date indication helper ***/
function DateAdder() {
    this.occupiedIntervals = []
    this.add = function(day, x, date, color) {
        // set text properties
        ctx.font = "14px verdana";
        ctx.fillStyle = color;
        ctx.textBaseline = "bottom";
        ctx.textAlign = "center";
        // get interval
        var textWidth = ctx.measureText(date).width;
        var interval = new Interval(x - textWidth/2, x + textWidth/2);
        // check if in existing interval
        for(var i = 0; i < this.occupiedIntervals.length; i++)
            if(this.occupiedIntervals[i].collidesWith(interval))
                return;
        // check if "now" is in interval
        var center_x = interpretedTimelineData.dayToPx(interpretedTimelineData.center_day);
        if(interval.has(center_x))
            return;
        // add text
        ctx.fillText(date, x, TIMELINE_BOTTOM_Y-10);
        // add interval
        this.occupiedIntervals.push(interval);
    }
}

/*** proposal height heilper ***/
function ProposalHeightHelper() {
    function Level() {
        this.occupiedIntervals = [];
        this.add = function(interval) {
            this.occupiedIntervals.push(interval);
        }
        this.collidesWith = function(interval) {
            for(var i = 0; i < this.occupiedIntervals.length; i++)
                if(this.occupiedIntervals[i].collidesWith(interval))
                    return true;
            return false;
        }
    }
    this.levels = [];
    this.addAndGetLevel = function(newInterval, lineX) {
        for(var l = 0; true; l++) {
            if(!this.levels[l])
                this.levels[l] = new Level();
            if(!this.levels[l].collidesWith(newInterval)) {
                this.levels[l].add(newInterval);
                // no overlap on line in all previous intervals
                line = new Interval(lineX-1, lineX+1);
                for(var ll = 0; ll < l; ll++)
                    this.levels[ll].add(line);
                return l;
            }
        }
    }
}

/*** link classes ***/
function Link(x, y, width, height, text, url, color, hoverColor) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.text = text;
    this.url = url;
    this.color = color;
    this.hoverColor = hoverColor;
    this.redraw = function(hover) {
        // rect to erase previous link
        ctx.fillStyle = BG_COL;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        // link
        Link.setStyle();
        ctx.fillStyle = hover ? this.hoverColor : this.color;
        ctx.fillText(this.text, this.x, this.y);
    }
}
Link.setStyle = function() { // static method
    ctx.font = PROPOSAL_FONT_SIZE+"px verdana";
    ctx.textBaseline = "top";
    ctx.textAlign = "left";
}
function Links() {
    this.links = Array();
    this.push = this.links.push;
    this.hoverLink = null;
    /*** check if the mouse is over the link and change cursor style ***/
    this.onMouseMove = function(event) {
        // Get the mouse position relative to the canvas element.
        var mouseX = event.pageX - canvas.offsetLeft;
        var mouseY = event.pageY - canvas.offsetTop;
        // go over all links
        var prevHoverLink = this.hoverLink;
        this.hoverLink = null;
        for(var i = 0; i < links.length; i++) {
            // is the mouse over a link?
            var lnk = links[i];
            if(mouseX >= lnk.x && mouseX <= (lnk.x+lnk.width) && mouseY >= lnk.y &&
                    mouseY <= (lnk.y+lnk.height)) {
                this.hoverLink = lnk;
                break;
            }
        }
        if(this.hoverLink) {
            document.body.style.cursor = "pointer";
        } else {
            document.body.style.cursor = "";
        }
        // redo link colors
        if(prevHoverLink != this.hoverLink) {
            if(this.hoverLink)
                this.hoverLink.redraw(true);
            if(prevHoverLink)
                prevHoverLink.redraw(false);
        }
    }
    /*** check if a link has been clicked ***/
    this.onClick = function(event) {
        if (this.hoverLink) {
            window.location = this.hoverLink.url;
        }
    }
}