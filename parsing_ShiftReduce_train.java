import java.io.*;
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
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.Word;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
/**
 * First use the tagger, then use the ShiftReduceParser.  
 * Note that ShiftReduceParser will not work on untagged text.
 *
 * @author John Bauer
 * Modified by Wang Junjie
 */
public class parsing_ShiftReduce_train {
        public static void main(String[] args) throws IOException {
                String modelPath = "edu/stanford/nlp/models/srparser/chineseSR.ser.gz";
                String taggerPath = "/nfs/nas-4.1/jjwang/stanford-postagger-full-2015-01-30/models/chinese-distsim.tagger";
                String textFile = "./Bangkok_negative_seg.out";
                String outFile = "./FullPasingResult_Bangkok_negative_seg.out";
                boolean dependencyFlag = false;
                String grammar = "edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz";
                String[] options = { "-maxLength", "1000"};
//                 String[] options = { "-maxLength", "1000" , "-tLPP", "edu.stanford.nlp.parser.lexparser.ChineseTreebankParserParams", 
// "-chineseFactored", "-encoding", "UTF-8",  "-tokenized", "-sentences", "newline", "-escaper", "edu.stanford.nlp.trees.international.pennchinese.ChineseEscaper"};
                LexicalizedParser lp = LexicalizedParser.loadModel(grammar, options);
                TreebankLanguagePack tlp = lp.getOp().langpack();
                GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();

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
                                case "-d":
                                        dependencyFlag = true;
                                        argIndex += 1;
                                        break;
                                default:
                                        throw new RuntimeException("Unknown argument " + args[argIndex]);
                        }
                }

                String text = "旅馆 在 小巷 子 里 ， 安全 没 问题 ， 但 附近 环境 确实 不 好 ， 有点 棚户区 的 感觉 ， 周围 没有 饭店 。";

                MaxentTagger tagger = new MaxentTagger(taggerPath);
                ShiftReduceParser model = ShiftReduceParser.loadModel(modelPath);

                InputStream is = new FileInputStream(textFile);
                String line; // Read in content of each line

                // String sql="sdfsdf";
                FileOutputStream fileOutputStream = new FileOutputStream(outFile); 
                // OutputStreamWriter oWriter = new OutputStreamWriter(fileOutputStream);
                // BufferedWriter bw = new BufferedWriter(oWriter);
                

                BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                line = reader.readLine(); // 读取第一行
                PrintStream ps = new PrintStream(fileOutputStream);
                System.setOut(ps);
                // DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(line));
                // tokenizer.setTokenizerFactory(null);

                while (line != null) { // 如果 line 为空说明读完了
                        // line = line.split("\n")[0];
                        // List<HasWord> sentence = Sentence.toWordList(line);
                        // tokenizer = DocumentPreprocessor(new StringReader(line));
                        DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(line));
                        tokenizer.setTokenizerFactory(null);
                        String[] end = {"\n"};
                        // tokenizer.setSentenceFinalPuncWords(end);
                        String sentenceDelimiter = System.getProperty("line.separator");
                        tokenizer.setSentenceDelimiter(sentenceDelimiter);
                        // System.out.println(sentence);
                        for (List<HasWord> sentence : tokenizer) {
                                // System.out.println(sentence);
                                List<TaggedWord> tagged = tagger.tagSentence(sentence);
                                Tree tree = model.apply(tagged);
                                if (dependencyFlag) {
                                        GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
                                        List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();
                                        System.out.println(tdl);
                                }
                                else {
                                        System.out.println(tree);       
                                }
                        }
                        line = reader.readLine(); // 读取下一行
                }
                reader.close();
                is.close();
        }
}
