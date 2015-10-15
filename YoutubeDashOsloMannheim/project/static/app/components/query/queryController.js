'use strict';

define(['app'], function (app) {

    
    app.register.controller('queryController', ['APIKeyService','queryService', '$rootScope','$routeParams', 
     function (APIKeyService,queryService, $rootScope, $routeParams) {

        var vm = this;
   
        
        vm.loadOldQueries = loadOldQueries;
        vm.createQuery = createQuery;
        vm.APIKeyList = [];
        vm.oldQueries = [];
        vm.maxOldQueries = {
        	    availableOptions: [
        	      {value: '10', name: '10'},
        	      {value: '20', name: '20'},
        	      {value: '30', name: '30'},
        	      {value: '40', name: '40'},
        	      {value: '40', name: '40'}
        	    ],
        	    selectedOption: {value: '10', name: '10'} //This sets the default value of the select in the ui
        	    };
        initController();
        
        
        function initController() {
            loadAllKeys();
            loadOldQueries();
            if(typeof $routeParams.hash !== 'undefined') {
            	loadHashQuery();
            }
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
        
        function loadHashQuery() {
        	queryService.getQuery($routeParams.hash)
        		.then(function (data) {
        			if(data.success===true)
        			{
        				vm.query = data.query;
        			}
        	});
        }
        
        function loadOldQueries() {
        	
        	queryService.getAll(vm.maxOldQueries.selectedOption.value)
    		.then(function (data) {
    			if(data.success===true)
    			{
    				vm.oldQueries = data.queries;
    			}
    	});
        }
        
        function createQuery() {
            vm.dataLoading = true;
            
            queryService.create(vm.query)
    		.then(function (response) {
    			if(response.success===true)
    			{
        			vm.loadOldQueries();
        			vm.dataLoading = false;
    			}
    			else {
    				vm.dataLoading = false;
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