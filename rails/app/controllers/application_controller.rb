# Filters added to this controller apply to all controllers in the application.
# Likewise, all the methods added will be available for all controllers.

class ApplicationController < ActionController::Base
  helper :all # include all helpers, all the time
  ActiveRecord::Base.include_root_in_json = false

  def self.syncs(methods, options)
    after_filter(:sync, :only => methods)
  end

  def sync
    # Add manifest to head
    onload_stub = '
<script type="text/javascript">
$(function() {
	posts = ' + @posts.to_json + ';
jQuery("body").render();	
});
</script>
'
    added_text = '<!-- start synckit -->
<link rel="stylesheet" type="text/css" href="/stylesheets/style.css" />
<script type="text/javascript" src="/javascripts/jquery-1.3.2.min.js"></script>
<script type="text/javascript" src="/javascripts/template.js"></script>
' + onload_stub + '
<!-- end synckit -->
' 

    self.response.body = self.response.body.gsub(/<\/head>/, "#{added_text}<\/head>")    
  end
  
  def analyze_method(method)
    arr = self.instance_variables
    eval(method)
    
  end
  
  # Just for testing, disable this.
  # protect_from_forgery # See ActionController::RequestForgeryProtection for details

  # Scrub sensitive parameters from your log
  # filter_parameter_logging :password
end
