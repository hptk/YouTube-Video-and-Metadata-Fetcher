"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var queryService = function ($http,$q) {

        var service = {};

        service.getAll = getAll;
        service.create = create;
        service.getQuery = getQuery;
        service.testQuery = testQuery;
        
        return service;

        function getAll(n) {
        	var deferred = $q.defer();
        	$http.get('/api/queries/list/'+n)
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
        
        function getQuery(hash) {
        	var deferred = $q.defer();
        	$http.get('/api/queries/'+hash)
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
        
        function create(query) {
            var deferred = $q.defer();
            $http.post('/api/queries', query)
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
        function ISODateString(d){
          	 function pad(n){return n<10 ? '0'+n : n}
          	 return d.getUTCFullYear()+'-'
          	      + pad(d.getUTCMonth()+1)+'-'
          	      + pad(d.getUTCDate())+'T'
          	      + pad(d.getUTCHours())+':'
          	      + pad(d.getUTCMinutes())+':'
          	      + pad(d.getUTCSeconds())+'Z'}
        
        function testQuery(query) {
        	var modQuery = angular.copy(query);
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

    queryService.$inject = injectParams;

    app.service('queryService', queryService);

});

