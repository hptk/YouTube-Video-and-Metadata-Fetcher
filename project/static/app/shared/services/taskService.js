"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var taskService = function ($http,$q) {

        var service = {};

        
        service.createTask = createTask;
        service.getProgress = getProgress;
        
        return service;

        
        function getProgress(url) {
        	var deferred = $q.defer();
        	$http.get(url)
                .success(function(data, status){
                	deferred.resolve(data);
                    
                })
                .error(function(data){
                    deferred.resolve({ success: false, message: 'Some Error' });
                });
            return deferred.promise;
        }
        
        function createTask(id,action) {
            var deferred = $q.defer();
            $http.post('/api/queries/'+id,{ action: action })
                .success(function(data, status){
                    if(data.success===true) {
                        deferred.resolve(data);
                    } else {
                        deferred.resolve(data);
                    }
                })
                .error(function(data){
                    deferred.resolve({ success: false, message: 'Some Error' });
                });

            return deferred.promise;
        }
        
        
        function testQuery(query) {
        	var modQuery = query;
        	if(modQuery.publishedBefore instanceof Date) {
        		modQuery.publishedBefore = ISODateString(modQuery.publishedBefore);
        	}
        	
        	if(modQuery.publishedAfter instanceof Date) {
        		modQuery.publishedAfter = ISODateString(modQuery.publishedAfter);
        	}
        	
        	var deferred = $q.defer();
        	gapi.client.setApiKey(modQuery.key);
            gapi.client.load('youtube', 'v3', function() {
            	modQuery.part="snippet";
                var request = gapi.client.youtube.search.list(modQuery);
                request.execute(function(response) {
                    deferred.resolve(response);
                });
            });
            return deferred.promise;
        }

 
    };

    taskService.$inject = injectParams;

    app.service('taskService', taskService);

});

