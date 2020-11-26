(function () {
  /**
   * Subscription API.
   * @param {String} url_prefix - URL prefix
   * @param {Function} callback - Session load callback
   */
  var Subscription = function (url_prefix, callback)
  {
    this.url_prefix = url_prefix;
    this.loadSession(callback);
  }

  /**
   * Retrieves curren session from server via API.
   * @param {Function} callback - Session load callback
   */
  Subscription.prototype.loadSession = function(callback)
  {
    var self = this;

    fetch(self.url_prefix + '/session/')
      .then(function (response) {
        response.json().then(function (data) {
          if (data.status == 'ok') {
            self.session = data.session;
          } else {
            console.error('Failed to load session');
          }

          callback(this);
        });
      });
  }

  /**
   * Creates subscription via API call using stripe token.
   * @param {String} stripeToken - Stripe token (f.e. "tok_.....")
   * @param {Number} plan_id - Subscription plan id (list of plans returned from session api)
   * @param {Function} on_success - Success handler.
   * @param {function} on_error - Error handler.
   */
  Subscription.prototype.subscribe = function (stripeToken, plan_id, on_success, on_error)
  {
    var formData = new FormData();
    var self = this;

    formData.append('csrfmiddlewaretoken', this.session.csrf_token);
    formData.append('stripe_token', stripeToken);
    formData.append('plan', plan_id);

    fetch(self.url_prefix + '/subscribe/', {
        method: "POST",
        body: formData
      })
      .then(function (response) {
        response.json().then(function (data) {
          if (data.status == 'ok') {
            on_success(data);
          } else {
            on_error(data);
          }
        });
      })
      .catch(function (error) {
        on_error(error);
        console.error(error);
      });
  };

  window.StripeSubscription = Subscription;
})();
