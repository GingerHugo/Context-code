
import java.io.StringReader;
import java.util.List;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.io.PrintStream;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.shiftreduce.ShiftReduceParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.Tree;

/**
 * First use the tagger, then use the ShiftReduceParser.  
 * Note that ShiftReduceParser will not work on untagged text.
 *
 * @author John Bauer
 * Modified by Wang Junjie
 */
public class parsing_ShiftReduce {
    public static void main(String[] args) throws IOException {
        String modelPath = "edu/stanford/nlp/models/srparser/chineseSR.ser.gz";
        String taggerPath = "/nfs/nas-4.1/jjwang/stanford-postagger-full-2015-01-30/models/chinese-distsim.tagger";
        String textFile = "./Bangkok_negative_seg.out";
        String outFile = "./FullPasingResult_Bangkok_negative_seg.out";

        for (int argIndex = 0; argIndex < args.length; ) {
            switch (args[argIndex]) {
                case "-tagger":
                    taggerPath = args[argIndex + 1];
                    argIndex += 2;
                    break;
                case "-model":
                    modelPath = args[argIndex + 1];
                    argIndex += 2;
                    break;
                case "-textFile":
                    textFile = args[argIndex + 1];
                    argIndex += 2;
                    break;
                case "-outFile":
                    outFile = args[argIndex + 1];
                    argIndex += 2;
                    break;
                default:
                    throw new RuntimeException("Unknown argument " + args[argIndex]);
            }
        }

        String text = "旅馆 在 小巷 子 里 ， 安全 没 问题 ， 但 附近 环境 确实 不 好 ， 有点 棚户区 的 感觉 ， 周围 没有 饭店 。";

        MaxentTagger tagger = new MaxentTagger(taggerPath);
        ShiftReduceParser model = ShiftReduceParser.loadModel(modelPath);

        InputStream is = new FileInputStream(textFile);
        String line; // 用来保存每行读取的内容

        // String sql="sdfsdf";
        FileOutputStream fileOutputStream = new FileOutputStream(outFile); 
        // OutputStreamWriter oWriter = new OutputStreamWriter(fileOutputStream);
        // BufferedWriter bw = new BufferedWriter(oWriter);
        

        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        line = reader.readLine(); // 读取第一行

        // PrintStream console = System.err;

        // File file = new File("err.txt");
        // FileOutputStream fos = new FileOutputStream(file);
        PrintStream ps = new PrintStream(fileOutputStream);
        System.setErr(ps);
        // System.err.println("This goes to err.txt");

        while (line != null) { // 如果 line 为空说明读完了
            DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(line));
            for (List<HasWord> sentence : tokenizer) {
                List<TaggedWord> tagged = tagger.tagSentence(sentence);
                Tree tree = model.apply(tagged);
                System.err.println(tree);
                // bw.write(tree);
            }
            line = reader.readLine(); // 读取下一行
        }
        // bw.flush();
        // bw.close();
        reader.close();
        is.close();
    }
}
