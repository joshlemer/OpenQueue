var app = angular.module('app', ['ngRoute', 'mgcrea.ngStrap'])//ui.bootstrap' ])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');

	})
	.config(['$routeProvider', function($routeProvider) {
	    $routeProvider
	    .when('/', {
	        controller: 'RoomListController',
	        controllerAs: 'list',
	        templateUrl: 'static/list.html'
	    })
	    .when('/rooms/:roomName', {
	        controller: 'RoomController',
	        controllerAs: 'room',
	        templateUrl: 'static/detail.html'
	    })
	    .when('/sup', {
	        controller: 'RoomAPIController',
	        template: '<strong></strong>'
	    });
	}])
    .controller('RoomController',['$http', '$routeParams','$scope', '$interval', function($http, $routeParams, $scope, $interval){
        console.log($routeParams);
        var value = this;
        value.title = [];


        $scope.loadRoom = function() {
            $http.get('/api/rooms/' + $routeParams.roomName).success(function(data){
                value.title=data;
                value.data = data;
                $scope.the_room = data;
            });
        };
        this.join = function(queueSlug) {
            $http.post('/api/queues/' + queueSlug + '/join/')
            .success( function(data) {
                $scope.loadRoom();
            });
        };

        var promise = $interval( $scope.loadRoom, 30000);

        $scope.loadRoom();

        $scope.$on('$destroy', function() {
            if(angular.isDefined(promise)) {
                $interval.cancel(promise);
                promise = undefined;
            }
        });

    }])
    .controller('NewRoomController', ['$scope', '$http', function($scope, $http) {
        $scope.submit = function(newroom) {
            $http.post('/api/rooms/', {
                data: newroom
            }).success(function() {
                location.reload();
            });
            console.log(newroom);
        };
    }])
    .controller('RoomListController', ['$http', function($http){
        var value = this;
        $http.get('/api/rooms/').success(function(data){
            value.data = data;
        });
    }])
    .controller('ResourceController', ['$http', '$scope', function($http, $scope){

        $scope.queue_element = $scope.resource.current_queue_element;

    }])
    .controller('QueueElementController', ['$http', '$scope', function($http, $scope){

        $scope.delete = function() {
            $http.delete('/api/queues/' + $scope.queue._id + '/queue_elements/' + $scope.queue_element._id).success( function(){
                $scope.loadRoom();
            });
        };

    }])
    .directive("customPopover", ["$popover", "$compile", function($popover, $compile) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var myPopover = $popover(element, {
                    title: 'My Title',
                    contentTemplate: '/static/hello.tpl.html',
                    html: true,
                    trigger: 'manual',
                    autoClose: true,
                    scope: scope
                });
                scope.showPopover = function() {
                    myPopover.show();
                }
            }
        }
    }]);
