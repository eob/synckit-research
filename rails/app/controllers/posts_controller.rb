class PostsController < ApplicationController
  syncs :index, :cache => [:template]

  # ------------------------------
  # NOTES
  # ------------------------------
  
  # Why the @-variables? (where is the Python-style data dictionary?)
  # ==========================
  # Note that the data for the template is the intersection
  # of the template-referenced variables and the instance
  # variables on the controller rendering the template. This is
  # a way to describe the "data set" as it would be provided to 
  # a templating language like Django's or Velocity
  
  # CONVENTION v. CONFIGURATION
  # ============================
  # You're asking them to change their behavior rather than change their
  # code. I.e. they have to name their variables carefully. It would be nice
  # if they ALSO didn't have to change their behavior. 
  #
  # Suggestion: the variable names only matter so we can link the data 
  # specifications to the template locations. We can figure that out
  # regardless of the name, and then just give it a new name "var123432" 
  # or whatever
  
  # SYNC
  # ==========================
  # Intercepting the SQL queries takes care of running it on the client side
  # but the sync step still needs them to be giving us hints. Or do they.. dun dun DUNNN!
  
  # COMPILATION
  # ============
  # Is this just compilation? Should this be treated as compilation instead?
  
  # DATA-DEPENDENT OPERATION
  # =========================
  # What if the SQL query depends on data? Is there a way to account for that?
  # If the URL completely specifies the operaion, can we hash on the URL? Or should
  # we just say we support REST endpoints and nothing else?
  def index
    @posts = Posts.find :all
    # render 'index'
  end
  
end
