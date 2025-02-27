import scala.io.Source
import java.io.PrintWriter
import play.api.libs.json._

object DataTransformer {
  def main(args: Array[String]): Unit = {
    if (args.length != 2) {
      println("Usage: DataTransformer <input_file> <output_file>")
      sys.exit(1)
    }
    val inputFile = args(0)
    val outputFile = args(1)
    
    // Read input JSON file.
    val jsonStr = Source.fromFile(inputFile).mkString
    val json = Json.parse(jsonStr)
    
    // For each order, compute the total (price * quantity) and add it to the JSON object.
    val transformed = json.as[JsArray].value.map { order =>
      val price = (order \ "price").as[Double]
      val quantity = (order \ "quantity").as[Int]
      val total = price * quantity
      order.as[JsObject] + ("total" -> JsNumber(total))
    }
    
    val resultJson = Json.toJson(transformed)
    val writer = new PrintWriter(outputFile)
    writer.write(Json.prettyPrint(resultJson))
    writer.close()
    
    println(s"Transformation complete. Output written to $outputFile")
  }
}
