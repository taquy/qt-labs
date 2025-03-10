<?php
require 'vendor/autoload.php';

use OpenTelemetry\API\Trace\TracerProviderInterface;
use OpenTelemetry\SDK\Common\Export\Http\PsrTransportFactory;
use OpenTelemetry\SDK\Logs\LoggerProvider;
use OpenTelemetry\SDK\Logs\Exporter\OtlpHttpExporter;
use OpenTelemetry\SDK\Logs\Processor\SimpleLogRecordProcessor;
use OpenTelemetry\SDK\Logs\Logger;
use OpenTelemetry\SDK\Trace\TracerProvider;
use OpenTelemetry\SDK\Trace\SpanProcessor\SimpleSpanProcessor;
use OpenTelemetry\SDK\Trace\SpanExporter\OtlpHttpExporter;
use OpenTelemetry\Context\Propagation\TextMapPropagator;

// OTLP Endpoint (Change this to match your collector)
$otlpEndpoint = 'http://localhost:4318/v1/traces';

// 🌟 Create OTLP Trace Exporter
$traceExporter = new OtlpHttpExporter(
    (new PsrTransportFactory())->create($otlpEndpoint, 'application/x-protobuf')
);

// 🌟 Setup Tracer
$tracerProvider = new TracerProvider(
    new SimpleSpanProcessor($traceExporter)
);
$tracer = $tracerProvider->getTracer('php-app');

// Start a trace
$span = $tracer->spanBuilder('sample-span')->startSpan();
$span->setAttribute('user.id', 12345);
$span->setAttribute('order.id', 'A123');
sleep(1); // Simulating work
$span->end();

echo "Trace sent to OTLP\n";

// 🌟 Setup Logger
$logExporter = new OtlpHttpExporter(
    (new PsrTransportFactory())->create($otlpEndpoint, 'application/x-protobuf')
);
$loggerProvider = new LoggerProvider(
    new SimpleLogRecordProcessor($logExporter)
);
$logger = $loggerProvider->getLogger('php-app');

// Log a message
$logger->log("INFO", "User logged in", ['user.id' => 12345]);

echo "Logs sent to OTLP\n";

?>