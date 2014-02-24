openerp.account.quickadd = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.account = instance.web.account || {};

    instance.web.views.add('tree_account_move_line_quickadd', 'instance.web.account.QuickAddListView');
    instance.web.account.QuickAddListView = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.journals = [];
            this.periods = [];
            this.accounts =[];
            this.current_account = null;
            this.current_journal = null;
            this.current_period = null;
            this.default_account = null;
            this.default_period = null;
            this.default_journal = null;
            this.current_journal_type = null;
            this.current_journal_currency = null;
            this.current_journal_analytic = null;
            
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            this.$el.parent().prepend(QWeb.render("AccountMoveLineQuickAdd", {widget: this}));
            
            this.$el.parent().find('.oe_account_select_journal').change(function() {
                    self.current_journal = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_account_select_period').change(function() {
                    self.current_period = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            
            this.$el.parent().find('.oe_account_select_account').change(function() {
            	self.current_account = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            
            this.$el.parent().find('.print_extract_button').click(function() {
            	//mod.call("print_extract", []).then(function(result) {
                //    console.log( result) ;
                //});
            	
            	var extraCss = "/account_move_line_extend/static/src/css/popup_extract.css";
            	var popClose = true;
            	var mode = "iframe";//iframe popup
            	var popTitle = "extract";
            	var options = {  'extraCss' : extraCss, 
            					 'popClose': popClose, 
            					 'mode': mode,
            					 'popTitle': popTitle,
            					 'popHt':1000,
            					 'popWt':800,
            					 'popX':200,
            					 'popY':200,
            				   };

                $('.oe_list').printArea(options);
            	//window.print();
            });
            
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_account_select_journal').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_account_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_account_select_account').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_account_select_journal').removeAttr('disabled');
                self.$el.parent().find('.oe_account_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_account_select_account').removeAttr('disabled');
            });
            var mod = new instance.web.Model("account.move.line", self.dataset.context, self.dataset.domain);
            
            mod.call("default_get", [['journal_id','period_id','account_id'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                //self.current_journal = result['journal_id'];
                //self.current_account = result['account_id'];
            });
            return tmp;
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var mod = new instance.web.Model("account.move.line", context, domain);
            return $.when(mod.call("list_journals", []).then(function(result) {
                self.journals = result;
            }),mod.call("list_periods", []).then(function(result) {
                self.periods = result;
            }),mod.call("list_accounts", []).then(function(result) {
                self.accounts = result;
            })).then(function () {
                var o;
                
                self.$el.parent().find('.oe_account_select_account').children().remove().end();
                self.$el.parent().find('.oe_account_select_account').append(new Option('', ''));
                for (var i = 0;i < self.accounts.length;i++){
                    //o = new Option(self.accounts[i][1], self.accounts[i][0]);
                    o = "<option value="+self.accounts[i][0]+">"+self.accounts[i][1]+"</option>"
                    self.$el.parent().find('.oe_account_select_account').append(o);
                } 
                self.$el.parent().find('.oe_account_select_account').val(self.current_account).attr('selected',true);
                
                self.$el.parent().find('.oe_account_select_journal').children().remove().end();
                self.$el.parent().find('.oe_account_select_journal').append(new Option('', ''));
                //console.log(self.current_journal);
                for (var i = 0;i < self.journals.length;i++){
                    o = new Option(self.journals[i][1], self.journals[i][0]);
                    if (self.journals[i][0] === self.current_journal){
                        self.current_journal_type = self.journals[i][2];
                        self.current_journal_currency = self.journals[i][3];
                        self.current_journal_analytic = self.journals[i][4];
                        $(o).attr('selected',true);
                    }
                    self.$el.parent().find('.oe_account_select_journal').append(o);
                }
                
                self.$el.parent().find('.oe_account_select_period').children().remove().end();
                self.$el.parent().find('.oe_account_select_period').append(new Option('', ''));
                for (var i = 0;i < self.periods.length;i++){
                    o = new Option(self.periods[i][1], self.periods[i][0]);
                    self.$el.parent().find('.oe_account_select_period').append(o);
                }    
                self.$el.parent().find('.oe_account_select_period').val(self.current_period).attr('selected',true);
                
                return self.search_by_journal_period();
            });
        },
        search_accounts: function(id){
        	var self = this;
        	console.log(self.accounts);
        	var size = self.accounts.length;
        	var account = -1;
        	for(var i=0; i<size; i++){
        		var line = self.accounts[i]; 
        		if(id == line[0]){
        			account = line[2];
        		}
        	}
        	var account_size = account.length;
        	var res = [];
        	for(var i=0; i<size; i++){
        		var line = self.accounts[i]; 
        		if(account == line[2].substr(0,account_size) ){
        			res.push(line[2]);
        		}
        	}
        	//console.log(res);	
        	return res;
        },
        search_by_journal_period: function() {
            var self = this;
            var domain = [];
            if (self.current_journal !== null) domain.push(["journal_id", "=", self.current_journal]);
            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);
            if (self.current_account !== null) {
            	var accounts_list = self.search_accounts(self.current_account);
            	domain.push(["account_id", "child_of", accounts_list]);
            }
          
            
            self.last_context["journal_id"] = self.current_journal === null ? false : self.current_journal;
            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;
            
            if(self.current_account === null){
            	delete self.last_context["account_id"];
            }
            else{
            	self.last_context["account_id"] = self.current_account;
            }
            
            self.last_context["journal_type"] = self.current_journal_type;
            self.last_context["currency"] = self.current_journal_currency;
            self.last_context["analytic_journal_id"] = self.current_journal_analytic;
            
            return self.old_search(new instance.web.CompoundDomain(self.last_domain, domain), self.last_context, self.last_group_by);
        },
    });
};
