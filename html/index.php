<?php 
// GPIO pin number
$pin = 21;
	
if (isset($_POST['brightness'])) { 

	$targetBrightness = ($_POST['brightness'] > 255) ? 255 : $_POST['brightness'];
	
	exec('/usr/bin/pigs p ' . $pin . ' ' . $targetBrightness);
	
	exit;
} 
if (isset($_POST['autoBrightness'])) {
	$json = json_decode(file_get_contents('/var/www/html/window.conf'));
	
	$json->auto = $_POST['autoBrightness'];
	
	file_put_contents('/var/www/html/window.conf', json_encode($json));
	
	if ($_POST['autoBrightness']) {
		exec('/home/pi/window.py');
	}

	echo exec('/usr/bin/pigs gdc ' . $pin);
	
	exit;
}

// Get current brightness value
$brightness = exec('/usr/bin/pigs gdc ' . $pin);

// Get auto-brightness setting
$isAutoBrightness = json_decode(file_get_contents('/var/www/html/window.conf'))->auto;
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>Smart Window</title>

    <!-- Bootstrap -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/custom.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
	<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
  </head>
  <body>

<nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Smart Window</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">Home</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    <div class="container">

      <div class="starter-template">
        <h3>Brightness</h3><output for="fader" id="volume"><?php echo round($brightness / 2.55) ?>%</output><br/><br/>
		
		<div class="divider"></div>
		<div style="width: 32px; padding-top: 8px; float: left;">
			<img src="/img/brightness-dim.png" height="32" />
		</div>
		<div style="width: 32px; float: right; padding-top: 8px; ">
			<img src="/img/brightness-bright.png" height="32" />
		</div>
		<div style="margin: 0 48px;">
			<input type="range" min="0" max="256" step="16" value="<?php echo $brightness ?>" id="fader" 
				oninput="outputUpdate(value)">
		</div>
		<div class="clearfix"></div><br/>
		<div class="divider"></div>
		
		<a href="#" class="btn btn-<?php echo ($isAutoBrightness) ? 'primary' : 'default' ?> pull-right" style="width: 33%" id="autobrightness">
			<span class="glyphicon glyphicon-ok"></span></a>
		<div style="margin-top: 5px; float: left;">Auto-Brightness</div>
        <br/><br/><br/>
        <div class="divider"></div>
        
        <script>
	       	function outputUpdate(vol) 
		   	{
				$('#volume').text(Math.round(vol / 2.55) + '%');
				
				if ($('#autobrightness').hasClass('btn-primary')) {
					$('#autobrightness').trigger('click');
				}
				
				$.ajax({
				  method: "POST",
				  url: "index.php",
				  data: { brightness: vol}
				});
			}
			
			function updateAutoBrightness() 
			{
				var elem = $('#autobrightness');
				
				elem.toggleClass('btn-primary btn-default');
				
				// Auto Brightness
				var isAuto = (elem.hasClass('btn-primary')) ? 1 : 0;
				
				$.ajax({
				  method: "POST",
				  url: "index.php",
				  data: { autoBrightness: isAuto}
				})
				.done(function( msg ) {
				    $('input[type=range]').val(msg);
				    $('#volume').text(Math.round(msg / 2.55) + '%');
				});
			}
			
			$('#autobrightness').on('click', updateAutoBrightness);
        </script>
        
      </div>
    </div><!-- /.container -->


    
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>
  </body>
</html>
