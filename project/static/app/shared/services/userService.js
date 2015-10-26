"use strict";

define(['app'], function (app) {

    var injectParams = ['$http', '$q'];

    var UserService = function ($http,$q) {

        var service = {};

        service.GetAll = GetAll;
        service.GetById = GetById;
        service.Create = Create;
        service.Update = Update;
        service.Delete = Delete;

        return service;

        function GetAll() {
            return $http.get('/api/users').then(handleSuccess, handleError('Error getting all users'));
        }

        function GetById(id) {
            var user;
            var deferred = $q.defer();
            $http.get('/api/users/' + id)
                .success(function (data) {
                    if(data.success===true)
                        user=data.user
                        deferred.resolve(user);
                })
            
            return deferred.promise;
        }


        function Create(user) {
            var deferred = $q.defer();
            $http.post('/api/users', user)
                .success(function(data, status){
                    if(data.result===true) {
                        deferred.resolve({ success: true });
                    } else {
                        user = false;
                        deferred.resolve({ success: false, message: 'Username "' + user.username + '" is already taken' });
                    }

                })
                .error(function(data){
                    user=false
                    deferred.resolve({ success: false, message: 'Some Error' });
                });

            return deferred.promise;
        }

        function Update(user) {
            var deferred = $q.defer();
            return $http.put('/api/users/' + user.id, user).then(handleSuccess, handleError('Error updating user'));
        }

        function Delete(id) {
            return $http.delete('/api/users/' + id).then(handleSuccess, handleError('Error deleting user'));
        }

        // private functions

        function handleSuccess(res) {
            
            return res.data;
        }

        function handleError(error) {
            
            return function () {
                return { success: false, message: error };
            };
        }
    };

    UserService.$inject = injectParams;

    app.service('UserService', UserService);

});

