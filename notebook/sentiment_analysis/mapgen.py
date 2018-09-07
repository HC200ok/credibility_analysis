import json
import numpy as np

def grouping(coords, radiuses, colors, dates):
    assert len(coords) == len(radiuses)
    assert len(radiuses) == len(colors)
    assert len(colors) == len(dates)
    
    results = {}
    
    for date in np.unique(dates):
        results[date] = {}
        for color in np.unique(colors):
            results[date][color] = []
            for i in range(len(coords)):
                if colors[i] == color and dates[i] == date:
                    results[date][color].append({"lat":coords[i][0], "lon":coords[i][1], "radius": radiuses[i]})
    return results

def grouping_2(coords, colors, dates, infos):
    assert len(coords) == len(colors)
    assert len(colors) == len(dates)
    assert len(dates) == len(infos)
    
    results = {}
    
    for date in np.unique(dates):
        results[date] = {}
        for color in np.unique(colors):
            results[date][color] = []
            for i in range(len(coords)):
                if colors[i] == color and dates[i] == date:
                    results[date][color].append({"lat":coords[i][0], "lng":coords[i][1], "info": infos[i]})
    return results


def grouping_3(coords, colors, dates, infos):
    assert len(coords) == len(colors)
    assert len(colors) == len(dates)
    assert len(dates) == len(infos)
    
    results = {}
    
    for date in np.unique(dates):
        results[date] = {}
        for color in np.unique(colors):
            results[date][color] = []
            for i in range(len(coords)):
                if colors[i] == color and dates[i] == date:
                    results[date][color].append({"lat":coords[i][0], "lng":coords[i][1], "info": infos[i]})
    return results



def write_header(f):
    f.write("""
<html>
<head>
<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<title>Google Maps</title>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization&sensor=true_or_false"></script>
<script type="text/javascript" src="https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/markerclusterer.js"></script>
<script type="text/javascript" src="https://rawgit.com/hassanlatif/google-map-chart-marker-clusterer/master/src/chart-markerclusterer.js"></script>
<style>
.slider {
    -webkit-appearance: none;  
    appearance: none;
    width: 80%;
    height: 25px; 
    background: #d3d3d3; 
    outline: none; 
    opacity: 0.7; 
    -webkit-transition: .2s; 
    transition: opacity .2s;
}
</style>
""")


    
    
def write_initializer(f, center, coords, radiuses, colors, dates):
    data = grouping(coords, radiuses, colors, dates)
    param_dict = {
        "center0": center[0], "center1":center[1],
        "data": json.dumps(data),
        "dates": json.dumps(np.unique(dates).tolist()),
        "colors": json.dumps(np.unique(colors).tolist())
    }
    
    f.write("""
<script type="text/javascript">
    var data = {data};
    dates = {dates};
    var colors = {colors};
    circles = {{}};
        
    function initialize() {{
        var centerlatlng = new google.maps.LatLng({center0},{center1});
        var myOptions = {{ zoom: 6, center: centerlatlng, mapTypeId: google.maps.MapTypeId.ROADMAP }};
        var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
        
        for (var i=0; i<dates.length; i++) {{
          circles[dates[i]] = []
          for (var j=0; j<colors.length; j++){{
            for (var k=0; k<data[dates[i]][colors[j]].length; k++){{
              var circle = new google.maps.Circle({{
                strokeColor: colors[j],
                strokeOpacity: 0.6,
                strokeWeight: 2,
                fillColor: colors[j],
                fillOpacity: 0.3,
                map: map,
                center: new google.maps.LatLng(data[dates[i]][colors[j]][k]['lat'], data[dates[i]][colors[j]][k]['lon']),
                radius: data[dates[i]][colors[j]][k]['radius']
              }});
              circles[dates[i]].push(circle);
            }}
          }}
        }}
        return [circles, dates];
    }}
</script>
<script type="text/javascript">
function all_visible_false(){{
    for(var i=0; i<dates.length; i++){{
        var target = circles[dates[i]]
        for(var j=0; j<target.length; j++){{
            target[j].setVisible(false);
        }}
    }}
}}

function target_visible_true(target){{
    for(var i=0; i<target.length; i++){{
        target[i].setVisible(true);
    }}
}}

function run(i){{
    all_visible_false();
    var target = circles[dates[parseInt(i)]];
    target_visible_true(target);
}}
</script>
""".format(**param_dict))
    
    
def write_initializer_2(f, center, coords, colors, dates, infos):
    data = grouping_2(coords, colors, dates, infos);
    param_dict = {
        "center0": center[0], "center1":center[1],
        "data": json.dumps(data),
        "dates": json.dumps(np.unique(dates).tolist()),
        "colors": ["orange", "blue", "green", "red", "gray", "purple"],
    }
    
    f.write("""
<script type="text/javascript">
var data = {data};
dates = {dates};
colors = {colors};
markers = {{}};
markerCluster = 0;
map = 0;
center = [{center0}, {center1}];

function initialize(){{
    var centerlatlng = new google.maps.LatLng(center[0],center[1]);
    var myOptions = {{ zoom: 6, center: centerlatlng, mapTypeId: google.maps.MapTypeId.ROADMAP }};
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    var infoWin = new google.maps.InfoWindow();

    for(var i=0;i<dates.length;i++){{
        markers[dates[i]] = {{}};
        for(var j=0;j<colors.length;j++){{
            markers[dates[i]][colors[j]] = data[dates[i]][colors[j]].map(function(location, i) {{
                var marker = new google.maps.Marker({{position: {{'lat':location['lat'], 'lng': location['lng']}}}});
                google.maps.event.addListener(marker, 'click', function(evt) {{
                    infoWin.setContent(location['info']);
                    infoWin.open(map, marker);
                }});
                return marker;
            }});
        }}
    }}

    markerCluster = new MarkerClusterer(map, markers[dates[0]][colors[0]],
        {{imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'}});
    return markers, markerCluster, dates, colors, map
}}

function refreshMap(target) {{
    if (markerCluster) {{
        markerCluster.clearMarkers();
        markerCluster.addMarkers(target)
	}}
}}

function run(i, j){{
    var target = markers[dates[parseInt(i)]][colors[parseInt(j)]];
    refreshMap(target);
}}
</script>
""".format(**param_dict))


def write_initializer_3(f, center, coords, colors, dates, infos):
    data = grouping_3(coords, colors, dates, infos);
    param_dict = {
        "center0": center[0], "center1":center[1],
        "data": json.dumps(data),
        "dates": json.dumps(np.unique(dates).tolist()),
        "colors": ["orange", "blue", "green", "red", "gray", "purple"]
    }
    
    f.write("""
<script type="text/javascript">
var data = {data};
dates = {dates};
colors = {colors};
markers = {{}};
markerCluster = 0;
map = 0;
center = [{center0}, {center1}];

emo_dict = {{"orange": "happy", "blue":"sad", "green":"disgust", "red":"angry", "gray":"fear", "purple":"surprise"}};

function initialize(){{
    var centerlatlng = new google.maps.LatLng(center[0],center[1]);
    var myOptions = {{ zoom: 6, center: centerlatlng, mapTypeId: google.maps.MapTypeId.ROADMAP }};
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    var infoWin = new google.maps.InfoWindow();
    
    var opt = {{"styles" : [
        {{textColor: "black", textSize: 15, height: 50, width: 50}},
        {{textColor: "black", textSize: 15, height: 75, width: 75}},                    
        {{textColor: "black", textSize: 15, height: 100, width: 100}},
        {{textColor: "black", textSize: 15, height: 150, width: 150}},                    
        {{textColor: "black", textSize: 15, height: 200, width: 200}}
    ],"legend": {{
        "happy" : colors[0],
        "sad" : colors[1],
        "disgust" : colors[2] ,
        "angry" : colors[3],
        "fear" : colors[4],
        "surprise" : colors[5]
    }}}};

    for(var i=0;i<dates.length;i++){{
        markers[dates[i]] = [];
        for(var j=0; j<colors.length; j++){{
            var tmp_data = data[dates[i]][colors[j]].map(function(location, i) {{
                    var emotion = colors[j];
                    var emotion_title = emo_dict[emotion];
                    var marker = new google.maps.Marker({{
                        title: emotion_title, 
                        position: {{'lat':location['lat'], 'lng': location['lng']}}
                    }});
                    google.maps.event.addListener(marker, 'click', function(evt) {{
                        infoWin.setContent(location['info']);
                        infoWin.open(map, marker);
                    }});
                    return marker;
            }});
            markers[dates[i]] = markers[dates[i]].concat(tmp_data);
        }}
    }}

    markerCluster = new MarkerClusterer(map, markers[dates[0]],opt);
    return markers, markerCluster, dates, colors, map;
}}

function refreshMap(target) {{
    if (markerCluster) {{
        markerCluster.clearMarkers();
        markerCluster.addMarkers(target)
	}}
}}

function run(i){{
    var target = markers[dates[parseInt(i)]];
    refreshMap(target);
}}

google.load("visualization", "1", {{"packages": ["corechart"]}});
</script>
""".format(**param_dict))



def write_footer(f, dates):
    ds = np.unique(dates).tolist()    
    f.write("""
</head>
<body style="margin:0px; padding:0px;" onload="initialize();run(0);">
    <div id="map_canvas" style="width: 100%; height: 70%;"></div>
    <input type="range" min="0" max="{}" value="0" class="slider" id="myRange">
    <div id="output"></div>
    <script type="text/javascript">
    var slider = document.getElementById("myRange");
    var output = document.getElementById("output");
    output.innerHTML = dates[parseInt(slider.value)];
    slider.oninput = function() {{
        output.innerHTML = dates[parseInt(this.value)];
        run(parseInt(this.value));
    }}
    </script>
</body>
</html>
""".format(len(ds)-1, ds[0]))


def write_footer_2(f, dates):
    ds = np.unique(dates).tolist()
    cs = ["喜び", "悲しみ", "気色悪い", "怒り", "怖い", "驚き"]
    select = "<select id='color'>"+''.join(["<option value='{}'>{}</option>".format(i,c) for i,c in enumerate(cs)]) +"</select>"
    f.write("""
</head>
<body style="margin:0px; padding:0px;" onload="initialize(); run(0, 0);">
    <div id="map_canvas" style="width: 100%; height: 70%;"></div>
    {}
    <input type="range" min="0" max="{}" value="0" class="slider" id="myRange">
    <div id="output"></div>
    <script type="text/javascript">
    var slider = document.getElementById("myRange");
    var output = document.getElementById("output");
    var color = document.getElementById("color");
    output.innerHTML = dates[parseInt(slider.value)];
    slider.oninput = function() {{
        output.innerHTML = dates[parseInt(this.value)];
        run(parseInt(this.value), parseInt(color.value));
    }}
    color.onchange = function(){{
        run(parseInt(slider.value), parseInt(color.value));    
    }}
    </script>
</body>
</html>
""".format(select, len(ds)-1, ds[0]))
    
def write_footer_3(f, dates):
    ds = np.unique(dates).tolist()
    f.write("""
</head>
<body style="margin:0px; padding:0px;" onload="initialize(); run(0);">
    <div id="map_canvas" style="width: 100%; height: 70%;"></div>
    <input type="range" min="0" max="{}" value="0" class="slider" id="myRange">
    <div id="output"></div>
    <script type="text/javascript">
    var slider = document.getElementById("myRange");
    var output = document.getElementById("output");
    var color = document.getElementById("color");
    output.innerHTML = dates[parseInt(slider.value)];
    slider.oninput = function() {{
        output.innerHTML = dates[parseInt(this.value)];
        run(parseInt(this.value));
    }}
    color.onchange = function(){{
        run(parseInt(slider.value));    
    }}
    </script>
</body>
</html>
""".format(len(ds)-1, ds[0]))
    
def plot(filename, center, coords, radiuses, colors, dates):
    try:
        with open(filename, "w") as f:
            write_header(f)
            write_initializer(f, center, coords, radiuses, colors, dates)
            write_footer(f, dates)
        return True
    except Exception as e:
        print(e)
        return False
    
def plot_2(filename, center, coords, colors, dates, infos):
    try:
        with open(filename, "w") as f:
            write_header(f)
            write_initializer_2(f, center, coords, colors, dates, infos)
            write_footer_2(f, dates)
        return True
    except Exception as e:
        print(e)
        return False
    
def plot_3(filename, center, coords, colors, dates, infos):
    try:
        with open(filename, "w") as f:
            write_header(f)
            write_initializer_3(f, center, coords, colors, dates, infos)
            write_footer_3(f, dates)
        return True
    except Exception as e:
        print(e)
        return False