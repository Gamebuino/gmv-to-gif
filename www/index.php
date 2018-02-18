<?php
include_once(realpath(dirname(__FILE__)).'/constants.php');

$json = json_decode(file_get_contents($UPLOAD_FILE), true);
$deltime = time() - (60*60);
foreach($json as $id => $ts) {
	if ($ts < $deltime) {
		exec('rm -rf '.escapeshellarg($UPLOAD_DIR.$id));
		unset($json[$id]);
	}
}
file_put_contents($UPLOAD_FILE, json_encode($json));
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Gamebuino GMV to Gif</title>
		<meta charset="utf-8">
		<script src="https://gamebuino.com/js/jquery-3.1.1.min.js" type="text/javascript"></script>
		<script type="text/javascript">
			function setStatus(s) {
				$('#status').text(s);
			}
			$(document).ready(function() {
				$('#up').submit(function(e) {
					e.preventDefault();
					var formData = new FormData();
					formData.append('up', this.up.files[0]);
					setStatus('Uploading...');
					$.ajax({
						url: 'convert.php?json',
						type: 'POST',
						data: formData,
						contentType: false,
						cache: false,
						processData: false,
						success: function(data) {
							setStatus('');
							$('#error').empty();
							$('#output').empty();
							if (data.success) {
								$('#output').append($('<img>').attr({
									src: data.gif_url,
									alt: 'screenshot',
								}));
							} else {
								$('#error').text(data.error);
							}
						},
						error: function(e, textStatus, errorThrown) {
							setStatus('');
							alert('ERROR: Something went wrong!');
							console.error(e);
							console.error(textStatus);
							console.error(errorThrown);
						},
					});
				});
			});
		</script>
	</head>
	<body>
		<p id="gif-warning">Created GIFs are automatically deleted within an hour, so be sure to download them! (rightclick -> save image as)</p>
		<div id="error">
			<?php echo htmlentities($_GET['error']??''); ?>
		</div>
		<div id="output">
			<?php
			if (isset($_GET['id'])) {
				echo '<img src="uploads/'.(int)$_GET['id'].'/out.gif" alt="screenshot">';
			}
			?>
		</div>
		<form id="up" action="convert.php" method="post" enctype="multipart/form-data">
			<input type="file" name="up" />
			<input type="submit" value="Submit" />
		</form>
		<div id="status"></div>
	</body>
</html>
