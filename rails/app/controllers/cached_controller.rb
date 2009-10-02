class CachedController < ApplicationController

  def item
    logger.info "Got request with params:" + params.to_xml
  end

  # /cached/manifest
  def manifest
    respond_to do |format|
      format.html {render :text => "I think this is html"}
      format.manifest {
        headers["Expires"] = "Fri, 30 Oct 2010 14:19:41 GMT"
        headers["Cache-Control"] = "max-age=3600, must-revalidate"
      }
    end
  end
  
end
