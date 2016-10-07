<html>
<head>
	<title>SearchBot</title>
	<style>
	input[type=text] {
   	 	background-color: white;
    	width:70%;
    	height:35px;
    	border: 2px solid #ccc;
    	border-radius: 4px;
   		font-size: 16px;
    	padding: 12px 20px 12px 12px;
    	margin-left:10%;
	}
	input[type=button], input[type=submit], input[type=reset] {
    	background-color:#EC7F1D;
    	border: none;
    	border-radius: 4px;
    	color: white;
    	text-decoration: none;
    	font-size:large;
    	text-align:center;
    	margin: 4px 2px;
    	cursor: pointer;
    	width:12%;
    	height:35px;
	}
	h1, h2 { 
		color: #EC7F1D; 
		font-family: Florence; 
		font-size:60px;
		font-style: italic;
		font-weight: normal;
		text-align: center; 
		margin-left:8%;
	}
	h2 {
		font-size:23px;
		margin-left:16%;
		padding-left:0;
		text-align:left;
	}
	table {
    	border-collapse: collapse;
    	width: 62%;
    	margin-left:15%;
    	border-radius:4px;
	}

	th, td {
    	text-align: left;
    	padding: 8px;
    	font-family: Arial;
	}

	tr:nth-child(even){
		background-color: #f2f2f2;
	}

	th {
    	background-color: #FFB14F;
    	color: white;
	}
	/*The code used to flip the logo image is from https://css-tricks.com/snippets/css/flip-an-image/*/
	img {
		height: 12%;
        -moz-transform: scaleX(-1);
        -o-transform: scaleX(-1);
        -webkit-transform: scaleX(-1);
        transform: scaleX(-1);
        filter: FlipH;
        -ms-filter: "FlipH";
	}
	</style>
</head>
<body>
<br>
<div id="header" style="float:top;">
<h1 id="myH1" style="display: inline; top:10;"><img src="images/colorbird.svg" alt="logo" style="display: inline;"/>SearchBot</h1>
</div>
<form method="post">
  <div id="searchbar">
  <input type="text" name="keywords" id="user_input" placeholder="Please Enter Your Search Phrase..">
  <input type="submit" name="search" value="search">
  </div>
</form>
{{!base}}

%if len(history) > 0:
	<h2>Common Searches:</h2>
	<table id="history">
		<tr>
			<th>Word</th>
			<th>Count</th>
		</tr>
%end
%for key, value in history.most_common(20):
	<tr>
		<td>{{key}}</td>
		<td>{{value}}</td>
	</tr>
%end
</table>
</body>
</html>
