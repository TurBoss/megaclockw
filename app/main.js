$(document).ready(function() {

	var overlay = jQuery('<div id="overlay"> </div>');

	overlay.appendTo(document.body)

	// Variables

	let default_50 = 7.60;
	let default_60 = 7.67;

	let video_mode = 0;
	let input_video_mode = 0;
	let new_video_mode = 0;

	let clock_freq = 0.0;
	let input_clock_freq = 10.0;
	let new_clock_freq = 0.0;

	let reset_game = false;
	let input_reset_game = false;
	let new_reset_game = false;

	// var systems_menu = $( "#system_menu" ).menu();

	// spinner
	var clock_spin = $("#clock_input").spinner({
		min: 5.00,
		max: 12.8,
		step: 0.01,
		numberFormat: "n4",
		spin: function(event, ui) {
			input_clock_freq = event.currentTarget.value
			this.val = input_clock_freq;
		},
		change: function(event, ui) {
			input_clock_freq = event.currentTarget.value;
			this.val = input_clock_freq;

		}
	});

	var current_page = 0;

	var clock_box = $(".clock_mode");
	var video_box = $(".video_mode");
	var reset_box = $("#reset_box");
	var set_box = $("#set_box");
	var save_box = $("#save_box");
	var wlan_settings = $(".wlan_settings");
	var wlan_ssid_input = $("#ssid_input");
	var wlan_scan = $(".wlan_scan");
	var ip_settings = $(".ip_settings");
	var static_input = $("#static_input");

	var default_50_button = $("#default_clock_50");
	var default_60_button = $("#default_clock_60");


	var eur_radio = $('#video_mode input[type=radio][id=eur]');
	var jap_radio = $('#video_mode input[type=radio][id=jap]');
	var usa_radio = $('#video_mode input[type=radio][id=usa]');
	var reset_check = $("#reset");
	var country = $("#country_input");
	var ssid = $("#ssid_input");
	var pwd = $("#password_input");
	var mode = "dhcp";
	var address = $("#address");
	var netmask = $("#netmask");
	var gateway = $("#gateway");
	var dns = $("#dns");


	$("#eur").checkboxradio();
	$("#jap").checkboxradio();
	$("#usa").checkboxradio();

	$("#dhcp").checkboxradio();
	$("#static").checkboxradio();

	clock_box.controlgroup();
	video_box.controlgroup();
	wlan_settings.controlgroup();
	wlan_scan.controlgroup();
	ip_settings.controlgroup();

	clock_box.show();
	video_box.show();
	reset_box.show();
	set_box.show();

	save_box.hide();
	wlan_settings.hide();
	wlan_scan.hide();
	ip_settings.hide();

	$("#results_table").on('click', '.btnSelect', function() {
		// get the current row
		var currentRow = $(this).closest("tr");

		var data = currentRow.find("td:eq(0)").text();
		wlan_ssid_input.val(data);

	});

	$('#video_mode input:radio[name=mode]').click(function() {

		var region = $(this).attr('id');
		// console.log(region);
		if (region === 'eur') {
			input_video_mode = 1;
		}
		else if (region === 'jap') {
			input_video_mode = 2;
		}
		else if (region === 'usa') {
			input_video_mode = 3;
		}
	});

	$('#ip_settings input:radio[name=ip_mode]').click(function() {
		mode = $(this).attr('id');

		if (mode === "dhcp") {
			static_input.hide();
		}
		else {
			static_input.show();
		}
	});

	default_50_button.click(function() {
		input_clock_freq = default_50;
		clock_spin.val(default_50);
	});

	default_60_button.click(function() {
		input_clock_freq = default_60;
		clock_spin.val(default_60);
	});

	var start_timer = null;
	var poll_interval = null;
	var ping_interval = null;
	var bg_interval = null;

	var ping_ack = true;

	let counter = 50;

	//  bg_interval = setInterval(function() {
	//      main_bg.style.x = counter+'px';
	//      main_bg.style.background_pos = counter+'px';
	//      counter -=1;
	//      if (counter < 0){
	//          counter = 50;
	//      }
	//  }, 100);

	// WebSocket
	function startWS() {

		clock_spin.value = input_clock_freq;

		clearTimeout(start_timer);
		clearInterval(poll_interval);
		clearInterval(ping_interval);

		ping_ack = true

		if ("WebSocket" in window) {
			console.log("Init success");

			// Let us open a web socket
			var ws = new WebSocket('ws://' + location.hostname + ":" + "1337" + '/ws');

			$("#config").on("click", function() {
				if (current_page == 0) {
					current_page = 1;

					$('#results_table tr').remove();
					ws.send("__scan__");
					clock_box.hide();
					video_box.hide();
					reset_box.hide();
					set_box.hide();

					save_box.show();
					wlan_settings.show();
					wlan_scan.show();
					ip_settings.show();
				}
				else {
					current_page = 0;
					clock_box.show();
					video_box.show();
					reset_box.show();
					set_box.show();

					save_box.hide();
					wlan_settings.hide();
					wlan_scan.hide();
					ip_settings.hide();
				}
			});


			function sendChanges() {
				input_reset_game = reset_check.prop("checked");

				var json_msg = {
					"console": {
						"video_mode": input_video_mode,
						"clock_freq": parseFloat(clock_spin.val().replace(',', '.')),
						"reset_game": input_reset_game
					}
				};

				var data;

				data = JSON.stringify(json_msg);

				// Web Socket is connected, send data using send()
				ws.send(data);

				console.log("Message sent...");
				console.log(json_msg);

				reset_check.prop('checked', false);
			};

			var save_button = $("#save_button").click(function(event) {
				var settings_msg = {
					"wlan": {
						"country": country.val(),
						"ssid": ssid.val(),
						"pwd": pwd.val(),
						"mode": mode,
						"address": address.val(),
						"netmask": netmask.val(),
						"gateway": gateway.val(),
						"dns": dns.val()
					}
				};
				var data = JSON.stringify(settings_msg);

				// console.log(data);
				// Web Socket is connected, send data using send()
				ws.send(data);
			});

			var set_button = $("#set_button").click(function(event) {
				sendChanges();
				pollData();
			});

			var cancel_button = $("#cancel_button").click(function(event) {
				input_video_mode = video_mode;

				if (video_mode === 1) {
					eur_radio.click();
				}
				else if (video_mode === 2) {
					jap_radio.click();
				}
				else if (video_mode === 3) {
					usa_radio.click();
				}

				input_clock_freq = clock_freq;

				clock_spin.val(clock_freq.toFixed(2));

				input_reset_game = reset_game;

				reset_check.prop("checked", false);
			});

			function pollData() {

				if (ws === null) {
					startWS();
					return;
				}
				ws.send("__poll__");
			};

			ws.onopen = function() {

				console.log("Connected!");

				// ping server timer
				ping_interval = setInterval(function() {
					if (ping_ack === false) {
						// console.log("NONONONO");
						clearInterval(ping_interval);
						overlay.appendTo(document.body)
					}
					else {
						// console.log("PING -->");
						ws.send("__ping__");
						ping_ack = false;
					}
				}, 10000);

				// poll server data
				pollData(); // hack to not wait for the timer in the first run

				poll_interval = setInterval(function() {
					pollData();
				}, 5000);

				overlay.remove();
			};

			ws.onmessage = function(event) {

				var received_msg;
				var valid_json = true;

				try {
					received_msg = jQuery.parseJSON(event.data);
				}
				catch (err) {
					valid_json = false;
					console.log("received text");
					console.log(event.data);
				}

				if (valid_json === true) {

					console.log("received data json");

					$.each(received_msg, function(main_key, value) {
						console.log(main_key);
						if (main_key === "console") {

							$.each(value, function(key, val) {
								console.log(key + " " + val);
								if (key === "video_mode") {
									new_video_mode = val;
									if (new_video_mode !== video_mode) {
										video_mode = new_video_mode;
										if (video_mode === 1) {
											// console.log("video 1");
											eur_radio.click();
										}
										else if (video_mode === 2) {
											// console.log("video 2");
											jap_radio.click();
										}
										else if (video_mode === 3) {
											// console.log("video 3");
											usa_radio.click();
										}
									}

								}
								else if (key === "clock_freq") {
									new_clock_freq = val;
									if (new_clock_freq !== clock_freq) {
										clock_freq = new_clock_freq
										clock_spin.val(function(i, v) { return parseFloat(v).toFixed(2); });
										clock_spin.val(clock_freq);
									}
								}
								else if (key === "reset_game") {
									new_reset_game = val;
									if (new_reset_game !== reset_game) {
										reset_game = new_reset_game;

									}
								}
							});
						}
						else if (main_key === "wlan") {
							$.each(value, function(key, val) {
								console.log(key + " " + value)

							});
						}

						else if (typeof main_key == "number") {
							$('#results_table').append('<tr><td>' + value + '</td><td><button class="btnSelect">Select</button></td></tr>');
						}
					});
				}

				else {
					var data = event.data;
					if (data === "__pong__") {
						// console.log("PONG <--")
						ping_ack = true;
					}
				}
			};

			ws.onclose = function() {
				// websocket is closed.
				console.log("Connection is closed...");
				start_timer = setTimeout(startWS, 6000)  // esp32 takes 6 secs to boot
				overlay.appendTo(document.body)
				startWS();
			};
		}
		else {
			// The browser doesn't support WebSocket
			alert("WebSocket NOT supported by your Browser!");
			overlay.appendTo(document.body)
		};
	}

	// Start the websocket
	startWS();
});

