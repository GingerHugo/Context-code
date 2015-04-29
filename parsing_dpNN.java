import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.nndep.DependencyParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.process.*;
import java.io.StringReader;
import java.util.List;

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
/**
* Demonstrates how to first use the tagger, then use the NN dependency
* parser. Note that the parser will not work on untagged text.
*
* @author Jon Gauthier
*/
public class parsing_dpNN {
        public static void main(String[] args) throws IOException {
                String modelPath = DependencyParser.DEFAULT_MODEL;
                String taggerPath = "edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger";
                String textFile = "./Segmented_Entry_negative_testing.txt";
                String outFile = "./DPResult_Segmented_Entry_negative_testing.txt";

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

                // String text = "沒有 不 太 滿意。";
                // String text = "房間 很 舒適，床 也 很 大。";
                // String text = "房间 很 舒适，床 也 很 大。\n风景 很好，很 安静， 住 得 很 舒服。";
                String text = "房间 很 舒适，床 也 很 大。";
                // String text = "房间 没有 舒适 的 床。";
                // String text = "I can almost always tell when movies use fake dinosaurs.";

                MaxentTagger tagger = new MaxentTagger(taggerPath);
                DependencyParser parser = DependencyParser.loadFromModelFile(modelPath);
                InputStream is = new FileInputStream(textFile);
                String line; // Read in content of each line
                FileOutputStream fileOutputStream = new FileOutputStream(outFile); 
                BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                line = reader.readLine(); // Read in first line
                PrintStream ps = new PrintStream(fileOutputStream);
                System.setOut(ps);
                while (line != null) { // If reading ends
                        DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(line));
                        // DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(text));
                        // TokenizerFactory<CoreLabel> ctbTokenizerFactory = 
                        // CHTBTokenizer.factory(new CoreLabelTokenFactory(), "untokenizable=noneKeep");
                        // TokenizerFactory<? extends HasWord> tokenizerFactory = WhitespaceTokenizer.factory();
                        // tokenizer.setTokenizerFactory(tokenizerFactory);
                        // String[] end = {"\n"};
                        // tokenizer.setSentenceFinalPuncWords(end);
                        // String sentenceDelimiter = System.getProperty("line.separator");
                        // tokenizer.setSentenceDelimiter(sentenceDelimiter);
                        for (List<HasWord> sentence : tokenizer) {
                                List<TaggedWord> tagged = tagger.tagSentence(sentence);
                                GrammaticalStructure gs = parser.predict(tagged);

                                // Print typed dependencies
                                // System.err.println(gs);
                                System.out.print(gs);
                                System.out.print('\n');
                        }
                        line = reader.readLine(); // 读取下一行
                }
                reader.close();
                is.close();
        }
}