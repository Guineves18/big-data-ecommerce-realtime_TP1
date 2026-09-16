import json
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.common.time import Time
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, FilterFunction, ReduceFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Duration

class ParseJsonMap(MapFunction):
    def map(self, value):
        try:
            return json.loads(value)
        except:
            return {}

class FilterViewItems(FilterFunction):
    def filter(self, value):
        return value.get('event_type') == 'view_item'

class MapToTuple(MapFunction):
    def map(self, value):
        # (product_id, 1)
        return (value.get('product_id'), 1)

class SumViews(ReduceFunction):
    def reduce(self, value1, value2):
        return (value1[0], value1[1] + value2[1])

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    # Usando event time
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

    # Lendo o log gerado (Flume pode gravar em um dir, ou lendo direto do HDFS)
    # Aqui vamos ler de um diretório monitorado (Streaming)
    # Na infra Docker, /app/gerador/ecommerce_events.log pode ser lido, ou o HDFS
    # Para simplificar no Flink 1.17, vamos simular a leitura do HDFS (text)
    
    # O path pode ser substituído pelo HDFS: hdfs://namenode:9000/ecommerce/raw/
    source_path = '/app/gerador/ecommerce_events.log'

    # Leitura do stream como texto
    stream = env.read_text_file(source_path)

    # 1. Parse JSON e extrair timestamp
    parsed_stream = stream.map(ParseJsonMap(), output_type=Types.PICKLED_BYTE_ARRAY()) \
                          .filter(lambda x: 'timestamp' in x)

    # 2. Definir Watermarks (tolerância de atraso de 5 segundos)
    # No PyFlink, extrair o timestamp ISO
    # Nota: Simplificado para PyFlink
    # parsed_stream = parsed_stream.assign_timestamps_and_watermarks(
    #     WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
    #     .with_timestamp_assigner(...)
    # )

    # 3. Filtrar cliques (view_item)
    views = parsed_stream.filter(FilterViewItems())

    # 4. Mapear para Tupla (Produto, 1)
    mapped = views.map(MapToTuple(), output_type=Types.TUPLE([Types.STRING(), Types.INT()]))

    # 5. Janela Deslizante (Sliding Window): Tamanho 10 mins, Desliza a cada 2 mins
    # Como as watermarks são complexas em PyFlink sem conectores java, no exemplo básico usamos ProcessingTime
    windowed = mapped.key_by(lambda x: x[0]) \
                     .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2))) \
                     .reduce(SumViews(), output_type=Types.TUPLE([Types.STRING(), Types.INT()]))

    # 6. Gravar no HBase (Simulado como print aqui para validar)
    # Na prática, usaria o Flink HBase Connector (add_sink) ou Table API
    windowed.print()

    env.execute("E-Commerce Streaming - Trending Topics")

if __name__ == '__main__':
    main()
