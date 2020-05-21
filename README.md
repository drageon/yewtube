set in supybot config:

`supybot.plugins.Youtube: True # Set for all channels`

`supybot.plugins.Youtube.client_id: <blank>` You could also just try putting it there?

`supybot.plugins.Youtube.developer_key: <key from cloud.google.com>`

youtube API access is required, make a google cloud project, go to APIs and Services,
'Create Credentials', then it'll make an api key, then you can restrict it to
YouTube Data API v3
