"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var queryService = function ($http,$q) {

        var service = {};

        service.getAll = getAll;
        service.create = create;
        service.getQuery = getQuery;
        
        
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
                        deferred.resolve({ success: true });
                    } else {
                        deferred.resolve({ success: false, message: 'The key is already registered' });
                    }
                })
                .error(function(data){
                    deferred.resolve({ success: false, message: 'Some Error' });
                });

            return deferred.promise;
        }

 
    };

    queryService.$inject = injectParams;

    app.service('queryService', queryService);

});

