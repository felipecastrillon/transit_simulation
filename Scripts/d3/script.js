
var data

//read in data from stops

d3.csv("stops.txt", function(data){

  console.log(data[0]);

  var margin = {top: 20, right: 15, bottom: 60, left: 60}
    , width = 1500 - margin.left - margin.right
    , height = 1500 - margin.top - margin.bottom;
      
  var x = d3.scale.linear()
          .domain([d3.min(data, function(d) { return d.stop_lon; }), d3.max(data, function(d) { return d.stop_lon; })])
          .range([ 0, width ]);
      
  var y = d3.scale.linear()
          .domain([d3.min(data, function(d) { return d.stop_lat; }), d3.max(data, function(d) { return d.stop_lat; })])
          .range([ height, 0 ]);
  
  var tooltip = d3.select('body').append('div')
    .style('position','absolute')
    .style('padding','0 10px')
    .style('backgound','white')
    .style('opacity',0)

  var chart = d3.select('body')
    .append('svg:svg')
    .attr('width', width + margin.right + margin.left)
    .attr('height', height + margin.top + margin.bottom)
    .attr('class', 'chart')

  var main = chart.append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
    .attr('width', width)
    .attr('height', height)
    .attr('class', 'main')   
          
  // draw the x axis
  var xAxis = d3.svg.axis()
    .scale(x)
    .orient('bottom');

  main.append('g')
    .attr('transform', 'translate(0,' + height + ')')
    .attr('class', 'main axis date')
    .call(xAxis);

  // draw the y axis
  var yAxis = d3.svg.axis()
    .scale(y)
    .orient('left');

  //draw data
  main.append('g')  
    .attr('transform', 'translate(0,0)')
    .attr('class', 'main axis date')
    .call(yAxis);

  var g = main.append("svg:g"); 
  
  var dot = g.selectAll("scatter-dots")
    .data(data)
    .enter().append("svg:circle")
        .attr("cx", function (d,i) { return x(d.stop_lon); } )
        .attr("cy", function (d) { return y(d.stop_lat); } )
        .attr("r", 4)
  
  //mouseon animation to print stop_id      
  dot.on("mouseover", function(d) {
          
    tooltip.transition()
    .style('opacity',.9)

    tooltip.html("stop_id ="  + d.stop_id)
      .style('left',(d3.event.pageX) + 'px')
      .style('top',(d3.event.pageY) + 'px')

    tempColor = this.style.fill;
    d3.select(this)
      .style('opacity',1)
      .style('fill','orange')
  });

  //mouseout animation to go back to original w
  dot.on('mouseout',function(d){
  d3.select(this)
    .style('opacity',1)
    .style('fill',tempColor)
})
         
            
})