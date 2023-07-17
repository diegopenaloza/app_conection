    
          // Opciones del slider
          var sliderOptions = {
            start: [2015, 2023],
            connect: true,
            step: 1,
            range: {
              'min': 2015,
              'max': 2023
            },
            tooltips: [
              {
                to: function(value) {
                  return parseInt(value);
                }
              },
              {
                to: function(value) {
                  return parseInt(value);
                }
              }
            ]
          };

          // Crear el slider
          var slider = document.getElementById('year-slider');
          noUiSlider.create(slider, sliderOptions);


          function sugerencias() {
            var valor = document.getElementById('valor').value;
          
            // Realizar una solicitud HTTP GET al backend para obtener las sugerencias
            axios.get('http://localhost:8000/sugerencias', { params: { valor: valor } })
              .then(response => {
                var sugerencias = response.data.sugerencias;
                var ruc = response.data.ruc;
          
                // Mostrar las sugerencias en el campo de entrada
                var datalist = document.getElementById('sugerencias-list');
                datalist.innerHTML = '';
                
                sugerencias.forEach((sugerencia, index) => {
                  var option = document.createElement('option');
                  option.value = sugerencia + '-'+ ruc[index];
                  option.setAttribute('data-ruc', ruc[index]);
                  
                  
                  datalist.appendChild(option);
                });
          
                // Actualizar el valor del campo de entrada con el RUC seleccionado
                document.getElementById('valor').addEventListener('input', function() {
                  var selectedOption = datalist.querySelector('option[value="' + this.value + '"]');
                  if (selectedOption) {
                    var selectedRuc = selectedOption.getAttribute('data-ruc');
                    // var selectedRuc = selectedOption.value;
                    document.getElementById('valor').setAttribute('ruc', selectedRuc);
                  } else {
                    document.getElementById('valor').removeAttribute('ruc');
                  }

                  
                });


              })
              .catch(error => {
                console.error(error);
              });
          }
          
          






          
          // Detectar cambios en el campo de entrada y llamar a fetchData()
          var input = document.getElementById('valor');
          input.addEventListener('input', sugerencias);

          
          

    function fetchData() {
    var valor = document.getElementById('valor').getAttribute('ruc');
    //   var valor = document.getElementById('valor').value;
      fetch('http://localhost:8000/data_accion?valor=' + valor)
        .then(response => response.json())
        .then(data => {
          var uniqueNodes = {};
          var connectionsCount = {}; // Objeto para almacenar el conteo de conexiones PROVEEDOR

          data.nodes.forEach(function (node) {
            uniqueNodes[node.id] = node;
            if (node.id === valor) {
              node.main = true;
            }
          });

          data.edges.forEach(function (edge) {
            if (edge.label === 'PROVEEDOR') {
              // Si la conexión tiene la característica label: 'PROVEEDOR'
              var fromNode = edge.from;
              var toNode = edge.to;

              // Incrementar el conteo de conexiones para el nodo final
              if (connectionsCount[toNode]) {
                connectionsCount[toNode]++;
              } else {
                connectionsCount[toNode] = 1;
              }
            }
          });

          var nodes = new vis.DataSet(Object.values(uniqueNodes));
          var edges = new vis.DataSet(data.edges);



          // Obtener el contenedor del gráfico
          var container = document.getElementById('mynetwork');

          // Actualizar el tamaño del nodo final de las conexiones PROVEEDOR
          Object.keys(connectionsCount).forEach(function (nodeId) {
            var node = nodes.get(nodeId);
            node.size = connectionsCount[nodeId] * 10; // Cambiar el tamaño del nodo según el conteo de conexiones
            nodes.update(node);
          });
          

          // Función para filtrar las relaciones según el año seleccionado en el slider
          function filterEdges() {
            var selectedYearRange = slider.noUiSlider.get();
            var selectedYearMin = parseInt(selectedYearRange[0]);
            var selectedYearMax = parseInt(selectedYearRange[1]);

            var filteredEdges = edges.get({
              filter: function (item) {
                var year = new Date(item.Fecha).getFullYear();
                return year >= selectedYearMin && year <= selectedYearMax;
              }
            });

            var filteredNodeIds = new Set();
            filteredNodeIds.add(1); // Agregar siempre el accionista (ID: 1)

            filteredEdges.forEach(function (edge) {
              filteredNodeIds.add(edge.from);
              filteredNodeIds.add(edge.to);
            });

            var filteredNodes = new vis.DataSet();
            nodes.forEach(function (node) {
              if (filteredNodeIds.has(node.id) || node.tipo === 'accionistas'|| node.label === 'INVERSION'   || (node.label === 'INVERSION' && new Date(node.Fecha).getFullYear() <= 2015)) {

                filteredNodes.add(node);
              }
            });

            

            var filteredData = {
              nodes: filteredNodes,
              edges: filteredEdges
            };

            network.setData(filteredData);

            // Estilo del accionista cuando no hay empresas en el rango de años seleccionado
            var accionistaNode = network.body.data.nodes._data[1];
            if (accionistaNode) {
              if (!filteredNodeIds.has(2) && !filteredNodeIds.has(3)) {
                accionistaNode.color = 'rgba(128, 128, 128, 0.5)'; // Color más opaco
              } else {
                accionistaNode.color = undefined; // Restaurar color predeterminado
              }
              network.body.emitter.emit('_dataChanged');
            }
          }

          // Evento que se activa al cambiar el valor del slider
          slider.noUiSlider.on('change', filterEdges);

          // Crear los datos iniciales del gráfico
          var initialData = {
            nodes: nodes,
            edges: edges
          };


          var options = {
            physics: {
              enabled: false,
              stabilization: {
                enabled: true,
                iterations: 2000, // Aumenta el número de iteraciones para acelerar la estabilización
                fit: true,
              },
            },


            
            edges: {
              label: {
                enabled: false,
                min: 10,
                max: 30,
              },
              smooth: false, // Desactivar las líneas curvas entre nodos
              color: {
                opacity: 0 // Establecer la opacidad del color de las aristas como 0 (transparente)
              },
              arrows: {
                to: {
                  enabled: false // Deshabilitar las flechas en las conexiones
                }
              },
              enabled: false // Habilitar los edges por defecto
            },
            nodes: {

              font: {
                size: 0, // Ajusta el tamaño de la fuente de las etiquetas según tus necesidades
              },
            },
            interaction: {
              hover: true,
              hoverConnectedEdges: false,
              tooltipDelay: 100, // Ajusta el tiempo de retraso en milisegundos antes de mostrar el título
            },
          };




         // Inicializar el gráfico
         var network = new vis.Network(container, initialData, options);
        });

        network.on("stabilizationProgress", function (params) {
          var maxWidth = 496;
          var minWidth = 20;
          var widthFactor = params.iterations / params.total;
          var width = Math.max(minWidth, maxWidth * widthFactor);
      
          document.getElementById("bar").style.width = width + "px";
          document.getElementById("text").innerText =
            Math.round(widthFactor * 100) + "%";
        });
        network.once("stabilizationIterationsDone", function () {
          document.getElementById("text").innerText = "100%";
          document.getElementById("bar").style.width = "496px";
          document.getElementById("loadingBar").style.opacity = 0;
          // really clean the dom element
          setTimeout(function () {
            document.getElementById("loadingBar").style.display = "none";
          }, 500);
        });
    }