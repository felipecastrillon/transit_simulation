//get mapbox.com public token 
L.mapbox.accessToken = 'pk.eyJ1IjoiZmVsaXBlY2FzdHJpbGxvbiIsImEiOiJjaWdqbGU4YnIwMDR1dTFrcnd6MzVvdTE4In0.CWuQbWZ4H-vqr1eP1yPeRg';

//get amp tiles
var mapboxTiles = L.tileLayer('https://api.mapbox.com/v4/mapbox.comic/{z}/{x}/{y}.png?access_token=' + L.mapbox.accessToken, {
    attribution: '<a href="http://www.mapbox.com/about/maps/" target="_blank">Terms &amp; Feedback</a>'
});

//create map
var map = L.map('map')
    .addLayer(mapboxTiles)
    .setView([33.778243, -84.370670], 16);

//create svg object 
var svg = d3.select(map.getPanes().overlayPane).append("svg");
var g = svg.append("g").attr("class", "leaflet-zoom-hide");

//read and print data points
d3.json("stops.geojson", function(collection) {

    featuresdata = collection.features
    //stream transform. transforms geometry before passing it to
    // listener. Can be used in conjunction with d3.geo.path
    // to implement the transform. 
    var transform = d3.geo.transform({
        point: projectPoint
    });

    //d3.geo.path translates GeoJSON to SVG path codes.
    //essentially a path generator. In this case it's
    // a path generator referencing our custom "projection"
    // which is the Leaflet method latLngToLayerPoint inside
    // our function called projectPoint
    var d3path = d3.geo.path().projection(transform);

    // From now on we are essentially appending our features to the
    // group element. We're adding a class with the line name
    // and we're making them invisible
    // these are the points that make up the path
    // they are unnecessary so I've make them
    // transparent for now
    var ptFeatures = g.selectAll("circle")
        .data(featuresdata)
        .enter()
        .append("circle")
        .attr("r", 3)
        .style("fill", "red")
        .style("opacity", "1");

       // when the user zooms in or out you need to reset
    // the view
    map.on("viewreset", reset);
    // this puts stuff on the map! 
    reset();

    // Reposition the SVG to cover the features.
    function reset() {
        var bounds = d3path.bounds(collection),
            topLeft = bounds[0],
            bottomRight = bounds[1];
	    console.log(bounds)

        // here you're setting some styles, width, heigh etc
        // to the SVG. Note that we're adding a little height and
        // width because otherwise the bounding box would perfectly
        // cover our features BUT... since you might be using a big
        // circle to represent a 1 dimensional point, the circle
        // might get cut off.
 
        ptFeatures.attr("transform",
            function(d) {
                return "translate(" +
                    applyLatLngToLayer(d).x + "," +
                    applyLatLngToLayer(d).y + ")";
            });

        // Setting the size and location of the overall SVG container
        svg.attr("width", bottomRight[0] - topLeft[0] + 120)
            .attr("height", bottomRight[1] - topLeft[1] + 120)
            .style("left", topLeft[0] - 50 + "px")
            .style("top", topLeft[1] - 50 + "px");
        // ptPath.attr("d", d3path);
        g.attr("transform", "translate(" + (-topLeft[0] + 50) + "," + (-topLeft[1] + 50) + ")");
    } // end reset   
    
    // Use Leaflet to implement a D3 geometric transformation.
    // the latLngToLayerPoint is a Leaflet conversion method:
    //Returns the map layer point that corresponds to the given geographical
    // coordinates (useful for placing overlays on the map).
    function projectPoint(x, y) {
        var point = map.latLngToLayerPoint(new L.LatLng(y, x));
        this.stream.point(point.x, point.y);
    } //end projectPoint
});

// similar to projectPoint this function converts lat/long to
// svg coordinates except that it accepts a point from our 
// GeoJSON
function applyLatLngToLayer(d) {
    var y = d.geometry.coordinates[1]
    var x = d.geometry.coordinates[0]
    return map.latLngToLayerPoint(new L.LatLng(y, x))
}
