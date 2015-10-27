"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var resultService = function ($http,$q) {

        var service = {};
        service.getResults = getResults;
        
        return service;
        
        function getResults(id,section) {
            var deferred = $q.defer();
        
            $http.get('/api/statistics/'+id+"/"+section)
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
    };

    resultService.$inject = injectParams;

    app.service('resultService', resultService);
});

