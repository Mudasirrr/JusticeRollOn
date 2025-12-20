
/*
Plugin Name: Justice RollOn Connector
Description: Connects WordPress with the JusticeRollOn Django backend via REST API.
Version: 1.0
Author: Mel_Group 1 Team"
*/

function jro_fetch_api($endpoint) {
  $api_base = 'http://127.0.0.1:8000/api/';
  $response = wp_remote_get($api_base . $endpoint);
  if (is_wp_error($response)) return [];
  return json_decode(wp_remote_retrieve_body($response), true);
}

xit
exit()
