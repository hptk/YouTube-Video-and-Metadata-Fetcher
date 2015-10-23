'use strict';

define(['app'], function (app) {

    
    app.register.controller('manageKeysController', ['APIKeyService', '$rootScope', 
     function (APIKeyService, $rootScope) {

        var vm = this;

        vm.APIKeyList = [];

        vm.deleteAPIKey = deleteAPIKey;
        vm.addAPIKey = addAPIKey;
        vm.checkAvailability = checkAvailability;
        initController();
        
        
        function initController() {
            loadAllKeys();
        }

        function addAPIKey() {
        	APIKeyService.create(vm.apikey)
    		.then(function (data) {
    			if(data.success===true)
    			{
    				loadAllKeys();
    			}
    	});
        }
        

        function loadAllKeys() {
        	APIKeyService.getAll()
        		.then(function (data) {
        			if(data.success===true)
        			{
        				vm.APIKeyList = data.keys;
        				angular.forEach(vm.APIKeyList,function(apikey) {
        					checkAvailability(apikey);
        				});
        			}
        	});
        }
     
        function deleteAPIKey(id) {
        	
        	APIKeyService.deleteKey(id)
    			.then(function (data) {
    				if(data.success===true)
    				{
    					loadAllKeys();
    				}
    			});
        }
        
        function checkAvailability(apikey) {
        	APIKeyService.checkAvailability(apikey.key)
        		.then(function (status) {
        			if(status)
        			{
        				apikey.availability=true;
        			}
        			else {
        				apikey.availability=false;
        			}
        	});
        }


     }]);
});