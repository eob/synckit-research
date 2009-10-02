# Be sure to restart your server when you modify this file.

# Your secret key for verifying cookie session data integrity.
# If you change this key, all old sessions will become invalid!
# Make sure the secret is at least 30 characters and all random, 
# no regular words or you'll be exposed to dictionary attacks.
ActionController::Base.session = {
  :key         => '_synckit-temp_session',
  :secret      => 'db08544ebb37c161c4a3b9101db30778b46313c69a39f7df1fe2a5b8e2e2055a5650563deb4bc65e57247e642c72202b16cd9b07e40f5e528668e0fd3d3e420a'
}

# Use the database for sessions instead of the cookie-based default,
# which shouldn't be used to store highly confidential information
# (create the session table with "rake db:sessions:create")
# ActionController::Base.session_store = :active_record_store
