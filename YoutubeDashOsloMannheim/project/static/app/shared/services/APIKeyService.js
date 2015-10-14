"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var APIKeyService = function ($http,$q) {

        var service = {};

        service.getAll = getAll;
        service.create = create;
        service.deleteKey = deleteKey;
        service.checkAvailability = checkAvailability;

        return service;

        function getAll() {
        	var deferred = $q.defer();
        	$http.get('/api/keys/list')
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

        function create(apikey) {
            var deferred = $q.defer();
            $http.post('/api/keys', apikey)
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


        function deleteKey(id) {
        	var deferred = $q.defer();
            $http.delete('/api/keys/'+id)
                .success(function(data, status){
                    if(data.success===true) {
                        deferred.resolve({ success: true });
                    } else {
                        deferred.resolve({ success: false, message: 'Error when tried to delete' });
                    }
                })
                .error(function(data){
                    deferred.resolve({ success: false, message: 'Some Error' });
                });

            return deferred.promise;
        }
        
        function checkAvailability(apikey) {
        	var deferred = $q.defer();

        	$http.get('https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&key='+apikey, {
        	    headers: {}
        	})
            .success(function(data, status){
                if(status===200) {
                    deferred.resolve(true);
                } else {
                	deferred.resolve(false);
                }
            })
            .error(function(data){
                deferred.resolve(false);
            });

        	return deferred.promise;
        }
    };

    APIKeyService.$inject = injectParams;

    app.service('APIKeyService', APIKeyService);

});

