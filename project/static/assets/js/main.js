require.config({
    baseUrl: 'static/app',
    urlArgs: 'v=1.0'
});

require(
    [
        'app',
        'shared/services/routeResolver',
        'shared/services/userService',
        'shared/services/APIKeyService',
        'shared/services/queryService',
        'shared/services/taskService',
        'shared/services/resultService',
        'shared/services/authenticationService',
        'shared/services/flashService',        
    ],
    function () {
        angular.bootstrap(document, ['youtubeApp']);
    });
